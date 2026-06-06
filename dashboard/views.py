from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from inventory.utils import (
    get_inventory_summary,
    get_low_stock_products,
    get_dead_stock_products
)
from sales.utils import get_daily_sales_summary
from sales.credit_utils import (
    get_total_outstanding_credit,
    get_top_debtors,
    get_customers_with_balances,
)


def is_manager(user):
    return user.groups.filter(name="Manager").exists()


# Dashboard view
@login_required
def dashboard_home(request):
    # Restrict access to managers only
    if not is_manager(request.user):
        return HttpResponseForbidden("Access denied")

    context = {
        'summary': get_inventory_summary(),
        'low_stock_products': get_low_stock_products(),
        'dead_stock_products': get_dead_stock_products(),
        'daily_sales': get_daily_sales_summary,
        'outstanding_credit': get_total_outstanding_credit(),
        'top_debtors': get_top_debtors(),
        'customers_with_balances': get_customers_with_balances(),
    }

    return render(request, 'dashboard/home.html', context)
