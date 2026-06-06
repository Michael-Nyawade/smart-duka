from django.shortcuts import render
from core.utils import get_user_shop
from inventory.models import Product

def product_list(request):
    # Get the shop associated with the current user
    shop = get_user_shop(request.user)

    # Filter products by the user's shop
    products = Product.objects.filter(shop=shop)

    # Render the product list template with the filtered products
    return render(request, "inventory/product_list.html", {"products": products})
