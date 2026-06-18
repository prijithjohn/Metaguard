from django.urls import path
from . import views

urlpatterns = [
    path("datasets/<int:dataset_id>/quality/", views.quality_detail, name="quality_detail"),
]
