from django.http import JsonResponse
from django.shortcuts import render, redirect


def homepage(request):
    """Homepage - redirects to dashboard"""
    return redirect("dashboard")


def health_view(request):
    return render(request, "common/health.html", {"status": "ok"})


def health_api(request):
    return JsonResponse({"status": "ok", "service": "MetaGuard"})
