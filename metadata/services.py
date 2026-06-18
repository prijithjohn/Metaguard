import pandas as pd
from django.core.exceptions import ValidationError
from datasets.models import Dataset
from datasets.utils import get_local_dataset_path, stream_dataset_chunks
from .models import DatasetColumn


class MetadataExtractionService:
    @staticmethod
    def _normalize_dtype(dtype):
        name = str(dtype).lower()
        if "int" in name:
            return "integer"
        if "float" in name:
            return "float"
        if "bool" in name:
            return "boolean"
        if "datetime" in name or "timestamp" in name:
            return "datetime"
        return "string"

    @staticmethod
    def extract_columns(dataset: Dataset):
        file_path = get_local_dataset_path(dataset.file)
        column_names = []
        null_counts = {}
        unique_values = {}
        dtype_map = {}
        row_count = 0

        try:
            for chunk in stream_dataset_chunks(file_path):
                if chunk.empty:
                    continue

                if not column_names:
                    column_names = list(chunk.columns)
                    unique_values = {column: set() for column in column_names}
                    dtype_map = {column: chunk[column].dtype for column in column_names}

                row_count += len(chunk)
                for column in column_names:
                    series = chunk[column]
                    null_counts[column] = null_counts.get(column, 0) + int(series.isna().sum())
                    if len(unique_values[column]) <= 100000:
                        unique_values[column].update(series.dropna().astype(str).tolist())
                    dtype_map[column] = dtype_map[column] if column in dtype_map else series.dtype

        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError("Unable to parse dataset file for metadata extraction.") from exc

        column_count = len(column_names)
        dataset.row_count = row_count
        dataset.column_count = column_count
        dataset.save(update_fields=["row_count", "column_count"])

        DatasetColumn.objects.filter(dataset=dataset).delete()
        metadata_objects = []
        for column_name in column_names:
            series_dtype = dtype_map.get(column_name, object)
            metadata_objects.append(
                DatasetColumn(
                    dataset=dataset,
                    column_name=column_name,
                    data_type=MetadataExtractionService._normalize_dtype(series_dtype),
                    null_count=null_counts.get(column_name, 0),
                    unique_count=len(unique_values.get(column_name, set())),
                    classification="",
                )
            )

        DatasetColumn.objects.bulk_create(metadata_objects)
        return dataset

    @staticmethod
    def extract_for_dataset(dataset_id):
        dataset = Dataset.objects.get(pk=dataset_id)
        return MetadataExtractionService.extract_columns(dataset)
