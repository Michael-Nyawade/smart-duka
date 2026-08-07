from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from core.decorators import allowed_roles
from core.utils import get_user_shop

from .models import Product
from .forms import ProductForm


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