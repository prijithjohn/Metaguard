from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("datasets/<int:dataset_id>/report/pdf/", views.dataset_report_pdf, name="dataset_report_pdf"),
]
