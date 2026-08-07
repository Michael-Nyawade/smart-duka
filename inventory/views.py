from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from core.decorators import allowed_roles
from core.utils import get_user_shop, for_current_shop

from .models import Product, StockMovement
from .forms import ProductForm, StockReceiveForm


@login_required
@allowed_roles(["MANAGER"])
def product_list(request):

    shop = get_user_shop(request.user)

    products = Product.objects.for_shop(shop).order_by("name")

    return render(
        request,
        "inventory/product_list.html",
        {
            "products": products
        }
    )


@login_required
@allowed_roles(["MANAGER"])
def product_create(request):

    shop = get_user_shop(request.user)

    if request.method == "POST":

        form = ProductForm(
            request.POST
        )

        if form.is_valid():

            product = form.save(commit=False)
            product.shop = shop
            product.save()

            return redirect("product_list")

    else:
        form = ProductForm()


    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "title": "Add Product"
        }
    )


@login_required
@allowed_roles(["MANAGER"])
def product_update(request, pk):

    shop = get_user_shop(request.user)

    product = get_object_or_404(
        Product,
        pk=pk,
        shop=shop
    )


    if request.method == "POST":

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():

            form.save()

            return redirect("product_list")

    else:
        form = ProductForm(instance=product)


    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "title": "Edit Product"
        }
    )


@login_required
def stock_receive(request):
    shop = get_user_shop(request.user)

    if request.method == "POST":
        form = StockReceiveForm(
            request.POST,
            shop=shop
        )

        if form.is_valid():
            movement = form.save(commit=False)

            movement.shop = shop
            movement.movement_type = "IN"

            movement.save()

            messages.success(
                request,
                "Stock received successfully."
            )

            return redirect(
                "product_list"
            )

    else:
        form = StockReceiveForm(
            shop=shop
        )

    return render(
        request,
        "inventory/stock_receive.html",
        {
            "form": form
        }
    )


@login_required
def stock_movement_list(request):

    movements = (
        for_current_shop(
            StockMovement.objects.all(),
            request.user
        )
        .select_related("product")
        .order_by("-created_at")
    )

    return render(
        request,
        "inventory/stock_movement_list.html",
        {
            "movements": movements
        }
    )


@login_required
def inventory_alerts(request):

    products = for_current_shop(
        Product.objects.all(),
        request.user
    )

    low_stock_products = [
        p for p in products
        if p.is_low_stock()
    ]

    reorder_products = [
        p for p in products
        if p.needs_reorder()
    ]

    dead_stock_products = [
        p for p in products
        if p.is_dead_stock()
    ]

    return render(
        request,
        "inventory/inventory_alerts.html",
        {
            "low_stock_products": low_stock_products,
            "reorder_products": reorder_products,
            "dead_stock_products": dead_stock_products,
        }
    )
