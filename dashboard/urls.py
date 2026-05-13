from django.urls import path
from .views import dashboard_home

# URLs for Dashboard
urlpatterns = [
    path('', dashboard_home, name='dashboard-home'),
]
