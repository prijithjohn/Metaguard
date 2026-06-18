from django.contrib import admin
from .models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "file_name", "uploaded_at", "row_count", "column_count", "risk_level")
    search_fields = ("name", "file_name")
    list_filter = ("risk_level",)
