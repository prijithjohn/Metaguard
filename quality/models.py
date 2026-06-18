from django.db import models
from datasets.models import Dataset


class QualityReport(models.Model):
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name="quality_report")
    missing_values = models.PositiveIntegerField(default=0)
    duplicates = models.PositiveIntegerField(default=0)
    invalid_records = models.PositiveIntegerField(default=0)
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quality report for {self.dataset.name}"
