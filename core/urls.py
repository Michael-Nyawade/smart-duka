from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),

    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/inventory-alerts/", views.inventory_alerts, name="inventory_alerts"),
]