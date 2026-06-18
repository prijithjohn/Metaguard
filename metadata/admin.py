from django.contrib import admin
from .models import DatasetColumn


@admin.register(DatasetColumn)
class DatasetColumnAdmin(admin.ModelAdmin):
    list_display = ("dataset", "column_name", "data_type", "null_count", "unique_count")
    search_fields = ("column_name", "data_type")
    list_filter = ("data_type",)
