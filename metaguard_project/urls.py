from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("common.urls")),
    path("datasets/", include("datasets.urls")),
    path("", include("metadata.urls")),
    path("", include("quality.urls")),
    path("", include("governance.urls")),
    path("", include("reports.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
