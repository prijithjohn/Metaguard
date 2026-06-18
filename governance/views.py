from django.shortcuts import get_object_or_404, render
from datasets.models import Dataset
from .models import SensitiveDataReport


def sensitive_detail(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    report = SensitiveDataReport.objects.filter(dataset=dataset).first()
    return render(request, "governance/detail.html", {"dataset": dataset, "report": report})
