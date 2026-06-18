from django.urls import path
from . import views

urlpatterns = [
    path("datasets/<int:dataset_id>/sensitive/", views.sensitive_detail, name="sensitive_detail"),
]
