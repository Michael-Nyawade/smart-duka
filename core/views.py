from django.shortcuts import render

from django.utils import timezone
from django.db.models import Sum, F
from datetime import date

from core.utils import get_user_shop
from sales.models import Sale, SaleItem
from inventory.models import Product


def dashboard_view(request):

    shop = get_user_shop(request.user)

    today = date.today()

    # Sales today
    sales_today = Sale.objects.filter(
        shop=shop,
        created_at__date=today
    )

    total_sales_count = sales_today.count()

    # Total revenue today
    total_revenue = sum(
        sale.total_amount() for sale in sales_today
    )

    # Total profit today
    total_profit = sum(
        sale.profit() for sale in sales_today
    )

    # Credit sales today
    credit_sales = sales_today.filter(payment_method='CREDIT')

    total_credit = sum(
        sale.total_amount() for sale in credit_sales
    )

    # Low stock products
    low_stock_products = Product.objects.filter(
        shop=shop,
        stock_quantity__lte=5
    )

    context = {
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_credit': total_credit,
        'low_stock_products': low_stock_products,
    }

    return render(request, 'dashboard/dashboard.html', context)