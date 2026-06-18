from django.shortcuts import get_object_or_404, render
from datasets.models import Dataset
from .models import QualityReport


def quality_detail(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    report = QualityReport.objects.filter(dataset=dataset).first()
    return render(request, "quality/detail.html", {"dataset": dataset, "report": report})
