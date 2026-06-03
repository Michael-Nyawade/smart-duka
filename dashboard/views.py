from django.shortcuts import render
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

# Dashboard view
def dashboard_home(request):

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
