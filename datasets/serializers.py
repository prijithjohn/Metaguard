from rest_framework import serializers
from .models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            "id",
            "name",
            "file_name",
            "uploaded_at",
            "row_count",
            "column_count",
            "quality_score",
            "risk_level",
            "file",
        ]
