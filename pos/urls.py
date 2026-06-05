from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos_home, name='pos_home'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('cart/increase/<int:product_id>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<int:product_id>/', views.decrease_qty, name='decrease_qty'),
    path('api/add-to-cart/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/update/', views.api_update_cart, name='api_update_cart'),
]
