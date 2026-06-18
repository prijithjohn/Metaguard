from django.contrib import admin
from .models import QualityReport


@admin.register(QualityReport)
class QualityReportAdmin(admin.ModelAdmin):
    list_display = ("dataset", "score", "missing_values", "duplicates", "invalid_records", "created_at")
    search_fields = ("dataset__name",)
    readonly_fields = ("created_at",)
