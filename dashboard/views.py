from django.shortcuts import render
from inventory.utils import get_inventory_summary, get_low_stock_products, get_dead_stock_products

# Dashboard view
def dashboard_home(request):

    context = {
        'summary': get_inventory_summary(),
        'low_stock_products': get_low_stock_products(),
        'dead_stock_products': get_dead_stock_products(),
    }

    return render(request, 'dashboard/home.html', context)
