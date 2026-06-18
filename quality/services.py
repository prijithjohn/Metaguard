import hashlib
import pandas as pd
from django.core.exceptions import ValidationError
from .models import QualityReport
from .utils import is_valid_email
from datasets.utils import get_local_dataset_path, stream_dataset_chunks


class QualityAnalysisService:
    @staticmethod
    def _normalize_value(value):
        if value is None or pd.isna(value):
            return ""
        return str(value).strip()

    @staticmethod
    def _fingerprint_row(row_values):
        raw = "||".join([QualityAnalysisService._normalize_value(v) for v in row_values])
        return hashlib.md5(raw.encode("utf-8", errors="ignore")).hexdigest()

    @staticmethod
    def _count_invalid_emails(series):
        invalid_count = 0
        for value in series:
            if value is None or pd.isna(value):
                continue
            value_str = str(value).strip()
            if value_str and not is_valid_email(value_str):
                invalid_count += 1
        return invalid_count

    @staticmethod
    def _count_empty_columns(column_names, nonempty_columns):
        return sum(1 for col in column_names if not nonempty_columns.get(col, False))

    @staticmethod
    def compute_score(missing, duplicates, invalid_emails, total_cells, empty_columns, column_count):
        if total_cells == 0 or column_count == 0:
            return 0.0

        missing_weight = 35
        duplicates_weight = 20
        invalid_weight = 30
        empty_columns_weight = 15

        missing_ratio = missing / total_cells
        duplicate_ratio = duplicates / total_cells
        invalid_ratio = invalid_emails / total_cells
        empty_column_ratio = empty_columns / max(column_count, 1)

        score = 100.0
        score -= missing_ratio * missing_weight
        score -= duplicate_ratio * duplicates_weight
        score -= invalid_ratio * invalid_weight
        score -= empty_column_ratio * empty_columns_weight
        return max(0.0, min(100.0, score))

    @staticmethod
    def analyze(dataset):
        file_path = get_local_dataset_path(dataset.file)

        total_rows = 0
        missing_values = 0
        invalid_emails = 0
        seen_hashes = set()
        nonempty_columns = {}
        column_names = []

        try:
            for chunk in stream_dataset_chunks(file_path):
                if chunk.empty:
                    continue

                if not column_names:
                    column_names = list(chunk.columns)

                total_rows += len(chunk)
                missing_values += int(chunk.isna().sum().sum())

                for column in chunk.columns:
                    if not chunk[column].dropna().replace("", pd.NA).dropna().empty:
                        nonempty_columns[column] = True
                    if "email" in column.lower():
                        invalid_emails += QualityAnalysisService._count_invalid_emails(chunk[column])

                for row in chunk.itertuples(index=False, name=None):
                    fingerprint = QualityAnalysisService._fingerprint_row(row)
                    if fingerprint in seen_hashes:
                        continue
                    seen_hashes.add(fingerprint)

            column_count = len(column_names)
            empty_columns = QualityAnalysisService._count_empty_columns(column_names, nonempty_columns)
            total_cells = total_rows * max(column_count, 1)
            duplicates = max(0, total_rows - len(seen_hashes))
            score = QualityAnalysisService.compute_score(
                missing_values,
                duplicates,
                invalid_emails,
                total_cells,
                empty_columns,
                column_count,
            )
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError("Unable to parse dataset file for quality analysis.") from exc

        report, _ = QualityReport.objects.update_or_create(
            dataset=dataset,
            defaults={
                "missing_values": missing_values,
                "duplicates": duplicates,
                "invalid_records": invalid_emails,
                "score": score,
            },
        )

        dataset.quality_score = score
        dataset.save(update_fields=["quality_score"])
        return report
