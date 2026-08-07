from django.urls import path
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

]