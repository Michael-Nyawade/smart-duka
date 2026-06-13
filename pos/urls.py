from django.urls import path
from . import views

urlpatterns = [
    # POS Home
    path('', views.pos_home, name='pos_home'),

    # Checkout Flow
    path("htmx/checkout/", views.htmx_checkout_form, name="htmx_checkout_form"),
    path("htmx/checkout/process/", views.htmx_process_checkout, name="htmx_process_checkout"),

    # Cart (session-based)
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('cart/increase/<int:product_id>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<int:product_id>/', views.decrease_qty, name='decrease_qty'),

    # HTMX Cart
    path("htmx/cart/add/", views.htmx_add_to_cart, name="htmx_add_to_cart"),

    # Product utilities
    path('products/partial/', views.pos_products_partial, name='pos_products_partial'),
    path('search/', views.pos_search_products, name='pos_search_products'),
]