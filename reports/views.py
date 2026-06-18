from django.core.cache import cache
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from datasets.models import Dataset
from governance.models import SensitiveDataReport
from .services import PdfReportService


def dashboard_view(request):
    if request.user.is_staff:
        cache_key = "dashboard_metrics_all"
    elif request.user.is_authenticated:
        cache_key = f"dashboard_metrics_{request.user.id}"
    else:
        cache_key = "dashboard_metrics_anon"

    force_refresh = request.GET.get('refresh') == '1'

    base_qs = Dataset.objects.all()
    if request.user.is_authenticated and not request.user.is_staff:
        base_qs = base_qs.filter(owner=request.user)

    metrics = None if force_refresh else cache.get(cache_key)
    if metrics is None:
        total_datasets = base_qs.count()
        quality_avg = base_qs.aggregate(avg_quality=Avg('quality_score'))['avg_quality'] or 0.0
        risk_breakdown = list(base_qs.values('risk_level').annotate(count=Count('id')).order_by('-count'))
        sensitive_count = SensitiveDataReport.objects.filter(dataset__in=base_qs, total_sensitive_columns__gt=0).count()
        low_quality_count = base_qs.filter(quality_score__lt=60).count()
        total_records = base_qs.aggregate(total=Sum('row_count'))['total'] or 0
        high_risk_count = base_qs.filter(risk_level__in=['Confidential', 'Restricted']).count()

        ranges = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]
        quality_distribution = []
        for low, high in ranges:
            if high == 100:
                count = base_qs.filter(quality_score__gte=low, quality_score__lte=high).count()
            else:
                count = base_qs.filter(quality_score__gte=low, quality_score__lt=high).count()
            quality_distribution.append({'range': f"{low}-{high}", 'count': count})

        trend = base_qs.annotate(day=TruncDate('uploaded_at')).values('day').annotate(count=Count('id')).order_by('day')
        upload_trend_labels = [entry['day'].strftime('%Y-%m-%d') for entry in trend][-7:]
        upload_trend_counts = [entry['count'] for entry in trend][-7:]

        metrics = {
            'total_datasets': total_datasets,
            'total_records': total_records,
            'quality_avg': quality_avg,
            'risk_breakdown': risk_breakdown,
            'sensitive_count': sensitive_count,
            'low_quality_count': low_quality_count,
            'high_risk_count': high_risk_count,
            'quality_distribution': quality_distribution,
            'upload_trend_labels': upload_trend_labels,
            'upload_trend_counts': upload_trend_counts,
        }
        cache.set(cache_key, metrics, 30)

    recent_datasets = base_qs.order_by('-uploaded_at')[:6].select_related('owner')

    context = {
        **metrics,
        'recent_datasets': recent_datasets,
    }

    return render(request, 'reports/dashboard.html', context)


def dataset_report_pdf(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    buffer = PdfReportService.build_dataset_report(dataset)
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="metaguard_dataset_{dataset.id}.pdf"'
    return response
