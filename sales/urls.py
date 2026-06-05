from django.urls import path
from .views import sale_receipt_view
from . import views

urlpatterns = [
    path('receipt/<str:receipt_number>/', sale_receipt_view, name='sale-receipt'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/add-payment/', views.add_payment, name='add_payment'),
]
