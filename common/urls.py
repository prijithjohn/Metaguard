from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("health/", views.health_view, name="health"),
    path("api/health/", views.health_api, name="health_api"),
]
