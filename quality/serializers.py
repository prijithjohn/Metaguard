from rest_framework import serializers
from .models import QualityReport


class QualityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityReport
        fields = [
            "id",
            "dataset",
            "missing_values",
            "duplicates",
            "invalid_records",
            "score",
            "created_at",
        ]
