from django.db import models
from datasets.models import Dataset


class DatasetColumn(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="columns")
    column_name = models.CharField(max_length=255)
    data_type = models.CharField(max_length=100)
    null_count = models.PositiveIntegerField(default=0)
    unique_count = models.PositiveIntegerField(default=0)
    classification = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["column_name"]
        unique_together = [("dataset", "column_name")]

    def __str__(self):
        return f"{self.dataset.name} - {self.column_name}"
