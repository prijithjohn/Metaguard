from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Dataset
from .services import DatasetImportService


def _get_user_dataset(request, dataset_id):
    queryset = Dataset.objects.all()
    if request.user.is_authenticated and not request.user.is_staff:
        queryset = queryset.filter(owner=request.user)
    return get_object_or_404(queryset, pk=dataset_id)


def upload_dataset(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        uploaded_file = request.FILES.get("file")

        if not name:
            messages.error(request, "Please provide a dataset name.")
        elif not uploaded_file:
            messages.error(request, "Please upload a CSV or JSON file.")
        else:
            try:
                user = request.user if request.user.is_authenticated else None
                dataset = DatasetImportService.import_dataset(name, uploaded_file, user=user)
                messages.success(request, "Dataset uploaded and queued for processing.")
                return redirect("dataset_detail", dataset_id=dataset.id)
            except ValidationError as exc:
                messages.error(request, str(exc))
            except Exception:
                messages.error(request, "Unable to queue dataset processing right now. Please try again later.")

    return render(request, "datasets/upload.html", {})


def dataset_detail(request, dataset_id):
    dataset = _get_user_dataset(request, dataset_id)
    return render(request, "datasets/detail.html", {"dataset": dataset})


@login_required
def dataset_delete(request, dataset_id):
    dataset = _get_user_dataset(request, dataset_id)
    if request.method == "POST":
        try:
            if dataset.file:
                dataset.file.delete(save=False)
            dataset.delete()
            messages.success(request, f"Dataset '{dataset.name}' deleted successfully.")
        except Exception:
            messages.error(request, "Unable to delete dataset. Please try again.")
        return redirect("dataset_history")

    messages.error(request, "Dataset deletion requires a POST request.")
    return redirect("dataset_detail", dataset_id=dataset.id)


def dataset_history(request):
    qs = Dataset.objects.order_by('-uploaded_at')
    if request.user.is_authenticated and not request.user.is_staff:
        qs = qs.filter(owner=request.user)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)

    risk = request.GET.get('risk')
    if risk:
        qs = qs.filter(risk_level=risk)

    min_quality = request.GET.get('min_quality')
    if min_quality:
        try:
            mq = float(min_quality)
            qs = qs.filter(quality_score__gte=mq)
        except ValueError:
            pass

    has_sensitive = request.GET.get('has_sensitive')
    if has_sensitive == '1':
        qs = qs.filter(sensitivity_report__total_sensitive_columns__gt=0)

    page_size = 10
    paginator = Paginator(qs, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "datasets/history.html", {"datasets": page_obj, "page_obj": page_obj})


def dataset_status_api(request, dataset_id):
    dataset = _get_user_dataset(request, dataset_id)
    return JsonResponse({
        "dataset_id": dataset.id,
        "status": dataset.status,
        "progress": dataset.progress_percent,
        "progress_percent": dataset.progress_percent,
        "quality_score": dataset.quality_score,
        "risk_level": dataset.risk_level,
        "processed_count": dataset.processed_count,
        "failed_count": dataset.failed_count,
        "total_count": dataset.row_count,
        "error_message": dataset.error_message,
    })
