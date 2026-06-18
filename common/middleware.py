import logging
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            logger.exception("Unhandled exception in request")
            if request.path.startswith("/api/") or request.headers.get("Accept") == "application/json":
                return JsonResponse({"error": "Internal server error"}, status=500)
            return render(request, "common/error.html", {"message": "Internal server error"}, status=500)
