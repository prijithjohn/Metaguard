from django.db import models
from datasets.models import Dataset


class SensitiveDataReport(models.Model):
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name="sensitivity_report")
    total_sensitive_columns = models.PositiveIntegerField(default=0)
    total_matches = models.PositiveIntegerField(default=0)
    scanned_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"Sensitive data report for {self.dataset.name}"


class SensitiveField(models.Model):
    report = models.ForeignKey(SensitiveDataReport, on_delete=models.CASCADE, related_name="sensitive_fields")
    column_name = models.CharField(max_length=255)
    sensitivity_type = models.CharField(max_length=100)
    match_count = models.PositiveIntegerField(default=0)
    sample_value = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-match_count", "column_name"]

    def __str__(self):
        return f"{self.column_name} ({self.sensitivity_type})"
