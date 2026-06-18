import json
import re
from collections import defaultdict

import pandas as pd
from django.core.exceptions import ValidationError
from .models import SensitiveDataReport, SensitiveField
from datasets.utils import get_local_dataset_path, stream_dataset_chunks


class SensitiveDataDiscoveryService:
    EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    SSN_PATTERN = re.compile(r"^(?:\d{3}-\d{2}-\d{4}|\d{9})$")
    CREDIT_CARD_PATTERN = re.compile(r"^(?:\d[ -]?){13,16}$")
    PHONE_PATTERN = re.compile(r"^(?:\+?\d{1,3}[ -]?)?(?:\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4})$")
    IPV4_PATTERN = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
    AADHAAR_PATTERN = re.compile(r"^\d{12}$")
    PAN_PATTERN = re.compile(r"^[A-Z]{5}\d{4}[A-Z]$", re.IGNORECASE)
    IFSC_PATTERN = re.compile(r"^[A-Za-z]{4}0[A-Z0-9]{6}$")
    UPI_PATTERN = re.compile(r"^[\w.\-]{2,}@[a-zA-Z]{2,}$")
    MOBILE_PATTERN = re.compile(r"^(?:\+91[\-\s]?)?[6-9]\d{9}$")
    DOB_PATTERN = re.compile(r"^(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})$")
    SALARY_PATTERN = re.compile(r"^[\$\u20B9]?\s?\d{1,3}(?:[,\.\s]\d{3})*(?:\.\d{1,2})?$")

    HEADER_KEYWORDS = {
        "Email": ["email", "e-mail"],
        "US SSN": ["ssn", "social security"],
        "Credit Card": ["credit card", "card number", "ccnum", "cc number"],
        "Phone Number": ["phone", "mobile", "telephone", "tel"],
        "IPv4 Address": ["ip", "ipv4", "ip_address"],
        "Aadhaar": ["aadhaar", "aadhar"],
        "PAN": ["pan", "pan_number", "pancard"],
        "IFSC": ["ifsc"],
        "UPI": ["upi", "vpa"],
        "DOB": ["dob", "date_of_birth", "birth"],
        "Salary": ["salary", "income", "pay", "ctc"],
        "Address": ["address", "addr", "location", "city", "state", "zip", "zipcode", "pincode"],
    }

    @staticmethod
    def _normalize_value(value):
        if value is None or pd.isna(value):
            return None
        return str(value).strip()

    @classmethod
    def _count_pattern_matches(cls, values, pattern):
        match_count = 0
        for value in values:
            normalized = cls._normalize_value(value)
            if normalized and pattern.match(normalized):
                match_count += 1
        return match_count

    @classmethod
    def _detect_column_sensitivity(cls, column_name, values):
        normalized_column = column_name.lower()
        candidates = [
            ("Email", cls.EMAIL_PATTERN),
            ("US SSN", cls.SSN_PATTERN),
            ("Credit Card", cls.CREDIT_CARD_PATTERN),
            ("Phone Number", cls.PHONE_PATTERN),
            ("Mobile", cls.MOBILE_PATTERN),
            ("Aadhaar", cls.AADHAAR_PATTERN),
            ("PAN", cls.PAN_PATTERN),
            ("IFSC", cls.IFSC_PATTERN),
            ("UPI", cls.UPI_PATTERN),
            ("Date of Birth", cls.DOB_PATTERN),
            ("Salary", cls.SALARY_PATTERN),
            ("IPv4 Address", cls.IPV4_PATTERN),
            ("Address", None),
        ]

        for sensitivity_type, pattern in candidates:
            header_keywords = cls.HEADER_KEYWORDS.get(sensitivity_type, [])
            header_match = any(keyword in normalized_column for keyword in header_keywords)
            if pattern is None:
                count = 0
            else:
                count = cls._count_pattern_matches(values, pattern)
            if count > 0 or header_match:
                sample_value = ""
                for value in values:
                    normalized = cls._normalize_value(value)
                    if normalized:
                        sample_value = normalized
                        break
                return sensitivity_type, max(count, 1), sample_value
        return None

    @classmethod
    def analyze(cls, dataset):
        file_path = get_local_dataset_path(dataset.file)
        candidate_columns = set()
        scans_remaining = defaultdict(lambda: 1000)
        detected = {}

        try:
            for chunk_index, chunk in enumerate(stream_dataset_chunks(file_path)):
                if chunk.empty:
                    continue

                if chunk_index == 0:
                    for column in chunk.columns:
                        normalized_column = column.lower()
                        if any(keyword in normalized_column for keywords in cls.HEADER_KEYWORDS.values() for keyword in keywords):
                            candidate_columns.add(column)
                        else:
                            candidate_columns.add(column)

                for column in list(candidate_columns):
                    if detected.get(column) is not None:
                        continue
                    if scans_remaining[column] <= 0:
                        continue
                    values = chunk[column].dropna().head(100).tolist()
                    detection = cls._detect_column_sensitivity(column, values)
                    if detection:
                        detected[column] = detection
                    scans_remaining[column] -= len(values)

                if all(detected.get(col) is not None or scans_remaining[col] <= 0 for col in candidate_columns):
                    break

        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError("Unable to parse dataset file for sensitive data discovery.") from exc

        report, _ = SensitiveDataReport.objects.update_or_create(
            dataset=dataset,
            defaults={
                "total_sensitive_columns": 0,
                "total_matches": 0,
            },
        )
        report.sensitive_fields.all().delete()

        total_matches = 0
        for column_name, (sensitivity_type, match_count, sample_value) in detected.items():
            SensitiveField.objects.create(
                report=report,
                column_name=column_name,
                sensitivity_type=sensitivity_type,
                match_count=match_count,
                sample_value=sample_value,
            )
            total_matches += match_count

        report.total_sensitive_columns = len(detected)
        report.total_matches = total_matches
        report.save()

        if report.total_sensitive_columns > 0 and not dataset.risk_level:
            dataset.risk_level = "Confidential"
            dataset.save(update_fields=["risk_level"])

        return report
