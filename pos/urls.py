from django.urls import path
from . import views

urlpatterns = [
    # POS Home
    path('', views.pos_home, name='pos_home'),

    # Checkout Flow
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),

    # Cart (session-based)
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('cart/increase/<int:product_id>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<int:product_id>/', views.decrease_qty, name='decrease_qty'),

    # AJAX Cart API
    path('api/add-to-cart/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/update/', views.api_update_cart, name='api_update_cart'),
    path("htmx/cart/add/", views.htmx_add_to_cart, name="htmx_add_to_cart"),

    # Product utilities
    path('products/partial/', views.pos_products_partial, name='pos_products_partial'),
    path('search/', views.pos_search_products, name='pos_search_products'),
]