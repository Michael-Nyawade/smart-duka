from django.urls import path
from . import views
from . import views


urlpatterns = [
    path(
        "products/",
        views.product_list,
        name="product_list"
    ),

    path(
        "products/add/",
        views.product_create,
        name="product_create"
    ),

    path(
        "products/<int:pk>/edit/",
        views.product_update,
        name="product_update"
    ),

    path(
        "stock/receive/",
        views.stock_receive,
        name="stock_receive"
    ),

    path(
        "stock/movements/",
        views.stock_movement_list,
        name="stock_movement_list"
    ),
]