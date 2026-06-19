import logging
import os
import pandas as pd
from django.core.exceptions import ValidationError
from .models import Dataset
from .utils import validate_csv_file, load_dataset_dataframe, get_valid_dataset_filename

logger = logging.getLogger(__name__)


class DatasetRowValidator:
    """Validates individual rows before processing. Fails fast with explicit errors."""

    @staticmethod
    def validate_row(row_dict, row_index):
        """Validate a single row. Returns (is_valid, error_message)."""
        errors = []

        if not row_dict or all(pd.isna(v) or (isinstance(v, str) and v.strip() == "") for v in row_dict.values()):
            errors.append("Row is completely empty/null")

        for col, val in row_dict.items():
            if val is None or pd.isna(val):
                continue
            try:
                if isinstance(val, float) and (val != val):
                    errors.append(f"Column '{col}' contains invalid float (NaN)")
                elif isinstance(val, (int, float)) and not (-1e10 < val < 1e10):
                    errors.append(f"Column '{col}' value out of bounds: {val}")
            except (TypeError, ValueError) as exc:
                errors.append(f"Column '{col}' value validation error: {str(exc)}")

        is_valid = len(errors) == 0
        error_msg = " | ".join(errors) if errors else None
        return is_valid, error_msg


class DatasetImportService:
    @staticmethod
    def import_dataset(name, uploaded_file, user=None):
        validate_csv_file(uploaded_file)
        uploaded_file.seek(0)

        safe_name = get_valid_dataset_filename(uploaded_file)

        dataset = Dataset(
            name=name,
            file=uploaded_file,
            file_name=safe_name,
            row_count=0,
            column_count=0,
            owner=user,
        )
        dataset.save()

        if dataset.file:
            dataset.file_name = os.path.basename(dataset.file.name)
            dataset.save(update_fields=["file_name"])

        from .tasks import process_dataset
        try:
            process_dataset(dataset.id)
        except Exception as exc:
            logger.error(
        f"Dataset processing failed: {str(exc)}",
        exc_info=True)
            dataset.status = "FAILED"
            dataset.error_message = str(exc)
            dataset.save(update_fields=["status", "error_message"])

        return dataset
