import json
import os
from collections import defaultdict

import pandas as pd
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename

ALLOWED_FILE_EXTENSIONS = {".csv", ".json"}
ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "application/json",
    "text/json",
    "application/octet-stream",
}
DEFAULT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024
DEFAULT_CHUNK_SIZE = int(getattr(settings, "METAGUARD_CHUNK_SIZE", 10000))
DEFAULT_MAX_UNIQUE_VALUES = int(getattr(settings, "METAGUARD_UNIQUE_VALUE_THRESHOLD", 100000))


def get_valid_dataset_filename(uploaded_file):
    return get_valid_filename(os.path.basename(uploaded_file.name))


def get_local_dataset_path(file_field):
    if hasattr(file_field, "path"):
        return file_field.path
    raise ValidationError("Dataset storage backend does not support local file access.")


def _validate_file_header(uploaded_file, extension):
    uploaded_file.seek(0)
    try:
        if extension == ".json":
            try:
                for _ in pd.read_json(uploaded_file, lines=True, chunksize=1):
                    break
            except ValueError:
                uploaded_file.seek(0)
                for _ in pd.read_json(uploaded_file, chunksize=1):
                    break
        else:
            pd.read_csv(uploaded_file, nrows=10, low_memory=False, on_bad_lines="error")
    finally:
        uploaded_file.seek(0)


def validate_dataset_upload(uploaded_file):
    extension = os.path.splitext(uploaded_file.name)[1].lower()
    if extension not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError("Only .csv and .json dataset files are accepted.")

    if uploaded_file.size == 0:
        raise ValidationError("Uploaded dataset file is empty.")

    max_size = getattr(settings, "METAGUARD_MAX_UPLOAD_SIZE", DEFAULT_MAX_UPLOAD_SIZE)
    if uploaded_file.size > max_size:
        raise ValidationError(
            f"Uploaded dataset exceeds maximum size of {max_size:,} bytes. "
            "Please submit a smaller file or use a pre-sampled dataset."
        )

    content_type = getattr(uploaded_file, "content_type", None)
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("Uploaded dataset content type is not permitted.")

    try:
        _validate_file_header(uploaded_file, extension)
    except Exception as exc:
        raise ValidationError(
            "Uploaded dataset is malformed or corrupted. Please upload a valid CSV or JSON file."
        ) from exc


def _read_json_chunks(file_path, chunk_size):
    try:
        for chunk in pd.read_json(file_path, lines=True, chunksize=chunk_size):
            yield chunk
        return
    except ValueError:
        for chunk in pd.read_json(file_path, chunksize=chunk_size):
            yield chunk


def stream_dataset_chunks(file_path, chunk_size=None):
    chunk_size = chunk_size or DEFAULT_CHUNK_SIZE
    lower_name = file_path.lower()

    if lower_name.endswith(".json"):
        yield from _read_json_chunks(file_path, chunk_size)
        return

    for chunk in pd.read_csv(
        file_path,
        chunksize=chunk_size,
        low_memory=False,
        encoding="utf-8",
        on_bad_lines="error",
    ):
        yield chunk


def count_dataset_rows(file_path, chunk_size=None):
    total = 0
    for chunk in stream_dataset_chunks(file_path, chunk_size=chunk_size):
        total += len(chunk)
    return total


def validate_csv_file(uploaded_file):
    """Legacy wrapper for backward compatibility. Calls validate_dataset_upload."""
    return validate_dataset_upload(uploaded_file)


def load_dataset_dataframe(file_path, chunk_size=None):
    """Legacy function for backward compatibility. Returns chunk generator via stream_dataset_chunks."""
    chunk_size = chunk_size or DEFAULT_CHUNK_SIZE
    return stream_dataset_chunks(file_path, chunk_size=chunk_size)


def estimate_column_statistics(file_path, chunk_size=None):
    first_chunk = True
    column_names = []
    nonempty_columns = defaultdict(bool)
    unique_values = defaultdict(set)
    row_count = 0

    for chunk in stream_dataset_chunks(file_path, chunk_size=chunk_size):
        if chunk.empty:
            continue

        if first_chunk:
            column_names = list(chunk.columns)
            first_chunk = False

        row_count += len(chunk)
        for column in column_names:
            column_data = chunk[column].dropna()
            if not column_data.empty:
                nonempty_columns[column] = True
                if len(unique_values[column]) <= DEFAULT_MAX_UNIQUE_VALUES:
                    unique_values[column].update(column_data.drop_duplicates().astype(str).tolist())

    return {
        "row_count": row_count,
        "column_names": column_names,
        "nonempty_columns": nonempty_columns,
        "unique_counts": {col: len(vals) for col, vals in unique_values.items()},
    }
