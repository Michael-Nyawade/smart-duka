"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from core.views import pos_login_view


def healthz(request):
    # Deliberately does no database work, so uptime pings keep the web
    # service awake without waking (and billing) the Neon database.
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("login/", pos_login_view, name="pos_login"),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("sales/", include("sales.urls")),
    path("pos/", include("pos.urls")),
    path("inventory/", include("inventory.urls")),
]