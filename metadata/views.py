from django.shortcuts import get_object_or_404, render
from datasets.models import Dataset
from .models import DatasetColumn


def metadata_detail(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    columns = DatasetColumn.objects.filter(dataset=dataset)
    return render(request, "metadata/detail.html", {"dataset": dataset, "columns": columns})
