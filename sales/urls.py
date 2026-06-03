from django.urls import path
from .views import sale_receipt_view

urlpatterns = [
    path('receipt/<str:receipt_number>/', sale_receipt_view, name='sale-receipt'),
]