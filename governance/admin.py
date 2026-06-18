from django.contrib import admin
from .models import SensitiveDataReport, SensitiveField


@admin.register(SensitiveDataReport)
class SensitiveDataReportAdmin(admin.ModelAdmin):
    list_display = ("dataset", "total_sensitive_columns", "total_matches", "scanned_at")
    search_fields = ("dataset__name",)
    readonly_fields = ("scanned_at",)


@admin.register(SensitiveField)
class SensitiveFieldAdmin(admin.ModelAdmin):
    list_display = ("column_name", "sensitivity_type", "match_count", "report")
    search_fields = ("column_name", "sensitivity_type")
    list_filter = ("sensitivity_type",)
