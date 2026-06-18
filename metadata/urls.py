from django.urls import path
from . import views

urlpatterns = [
    path("datasets/<int:dataset_id>/metadata/", views.metadata_detail, name="metadata_detail"),
]
