import os
import logging
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.core.exceptions import ValidationError

from datasets.utils import count_dataset_rows, get_local_dataset_path, stream_dataset_chunks

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(OSError, IOError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
)
def process_dataset(self, dataset_id):
    dataset = None
    try:
        from .models import Dataset
        from .services import DatasetRowValidator
        from governance.services import SensitiveDataDiscoveryService
        from quality.services import QualityAnalysisService
        from metadata.services import MetadataExtractionService

        dataset = Dataset.objects.get(pk=dataset_id)
        dataset.status = "PROCESSING"
        dataset.progress_percent = 0
        dataset.error_message = None
        dataset.processed_count = 0
        dataset.failed_count = 0
        dataset.save(update_fields=["status", "progress_percent", "error_message", "processed_count", "failed_count"])

        file_path = get_local_dataset_path(dataset.file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file missing on disk: {file_path}")

        total_rows = count_dataset_rows(file_path)
        dataset.row_count = total_rows
        dataset.save(update_fields=["row_count"])

        if total_rows == 0:
            logger.warning("Dataset %d has no rows", dataset_id)

        chunk_size = int(getattr(dataset, "chunk_size", 10000))
        processed_rows = 0
        failed_rows = 0
        failed_row_indices = []

        for chunk_idx, chunk in enumerate(stream_dataset_chunks(file_path, chunk_size=chunk_size)):
            if chunk.empty:
                continue

            for row in chunk.itertuples(index=False, name=None):
                row_data = dict(zip(chunk.columns, row))
                try:
                    is_valid, validation_error = DatasetRowValidator.validate_row(row_data, processed_rows)
                    if not is_valid:
                        failed_rows += 1
                        failed_row_indices.append((processed_rows, validation_error or "Row validation failed"))
                        logger.warning(
                            "Row validation failed: dataset=%d row_idx=%d error=%s",
                            dataset_id,
                            processed_rows,
                            validation_error,
                        )
                    processed_rows += 1
                except Exception as row_exc:
                    failed_rows += 1
                    failed_row_indices.append((processed_rows, str(row_exc)))
                    logger.error(
                        "Exception processing row: dataset=%d row_idx=%d error=%s",
                        dataset_id,
                        processed_rows,
                        str(row_exc),
                        exc_info=True,
                    )
                    processed_rows += 1
                    continue

            progress = 100 if total_rows == 0 else min(99, int(processed_rows / float(total_rows) * 100))
            dataset.progress_percent = progress
            dataset.processed_count = processed_rows
            dataset.failed_count = failed_rows
            dataset.save(update_fields=["progress_percent", "processed_count", "failed_count"])

            logger.info(
                "Chunk processed: dataset=%d chunk=%d rows=%d processed=%d failed=%d progress=%d%%",
                dataset_id,
                chunk_idx,
                len(chunk),
                processed_rows,
                failed_rows,
                dataset.progress_percent,
            )

        try:
            MetadataExtractionService.extract_columns(dataset)
        except Exception as metadata_exc:
            logger.warning(
                "Metadata extraction failed: dataset=%d error=%s",
                dataset_id,
                str(metadata_exc),
            )
            raise

        try:
            quality_report = QualityAnalysisService.analyze(dataset)
        except Exception as quality_exc:
            logger.error(
                "Quality analysis failed: dataset=%d error=%s",
                dataset_id,
                str(quality_exc),
                exc_info=True,
            )
            dataset.status = "FAILED"
            dataset.error_message = f"Quality analysis failed: {str(quality_exc)}"
            dataset.save(update_fields=["status", "error_message"])
            return {
                "status": "failed",
                "dataset_id": dataset.id,
                "total_rows": total_rows,
                "processed": processed_rows,
                "failed": failed_rows,
            }

        try:
            SensitiveDataDiscoveryService.analyze(dataset)
        except Exception as governance_exc:
            logger.warning(
                "Sensitive data discovery failed: dataset=%d error=%s",
                dataset_id,
                str(governance_exc),
            )

        dataset.quality_score = quality_report.score
        dataset.status = "COMPLETED"
        dataset.progress_percent = 100
        dataset.processed_count = processed_rows
        dataset.failed_count = failed_rows
        dataset.processed_at = timezone.now()
        dataset.save(update_fields=[
            "quality_score",
            "status",
            "progress_percent",
            "processed_count",
            "failed_count",
            "processed_at",
        ])

        if failed_rows > 0:
            logger.warning(
                "Dataset processing completed with failures: dataset=%d total=%d processed=%d failed=%d first_5_failures=%s",
                dataset_id,
                total_rows,
                processed_rows,
                failed_rows,
                failed_row_indices[:5],
            )

        return {
            "status": "completed",
            "dataset_id": dataset.id,
            "total_rows": total_rows,
            "processed": processed_rows,
            "failed": failed_rows,
            "quality_score": quality_report.score,
        }

    except Exception as exc:
        if dataset:
            try:
                dataset.status = "FAILED"
                dataset.error_message = f"Unexpected error: {str(exc)}"
                dataset.save(update_fields=["status", "error_message"])
            except Exception:
                logger.exception("Failed to update dataset status on error: dataset=%s", dataset_id if dataset else "unknown")

        logger.exception("process_dataset failed: dataset=%s error=%s", dataset_id if dataset else "unknown", str(exc))

        if isinstance(exc, (FileNotFoundError, IOError)):
            raise self.retry(exc=exc, countdown=30)

        raise
