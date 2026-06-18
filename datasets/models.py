from django.conf import settings
from django.db import models


class Dataset(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasets",
        db_index=True,
    )
    RISK_LEVEL_CHOICES = [
        ("Public", "Public"),
        ("Internal", "Internal"),
        ("Confidential", "Confidential"),
        ("Restricted", "Restricted"),
    ]

    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="datasets/")
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.PositiveIntegerField(default=0)
    column_count = models.PositiveIntegerField(default=0)
    # Ingestion status fields for async pipeline
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", db_index=True)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    quality_score = models.FloatField(null=True, blank=True, db_index=True)
    risk_level = models.CharField(max_length=50, choices=RISK_LEVEL_CHOICES, blank=True, db_index=True)
    # Track row-level processing results
    processed_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["uploaded_at"]),
            models.Index(fields=["risk_level"]),
            models.Index(fields=["quality_score"]),
        ]

    def __str__(self):
        return self.name
