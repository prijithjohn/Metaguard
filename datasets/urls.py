from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_dataset, name="upload_dataset"),
    path("history/", views.dataset_history, name="dataset_history"),
    path("<int:dataset_id>/", views.dataset_detail, name="dataset_detail"),
    path("<int:dataset_id>/delete/", views.dataset_delete, name="dataset_delete"),
    path("<int:dataset_id>/status/", views.dataset_status_api, name="dataset_status_api"),
]
