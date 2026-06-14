from django.db import models
from .models import Product

# Inventory insights functions
def get_low_stock_products():
    return Product.objects.filter(
        # stock_quantity__lte is same as 'stock_quantity <= low_stock_threshold'
        # .F() ==> compare using another database field
        stock_quantity__lte=models.F('low_stock_threshold'),
        stock_quantity__gt=0
    )


def get_dead_stock_products():
    return [
        product for product in Product.objects.all()
        if product.is_dead_stock()
    ]


def get_inventory_summary():

    products = Product.objects.all()

    total_products = products.count()

    low_stock_count = get_low_stock_products().count()

    dead_stock_count = len(get_dead_stock_products())

    total_stock_items = sum(
        product.stock_quantity for product in products
    )

    return {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'dead_stock_count': dead_stock_count,
        'total_stock_items': total_stock_items,
    }
