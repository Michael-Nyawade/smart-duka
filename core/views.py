from datetime import date

from django.shortcuts import render
from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField
from django.db.models.functions import ExtractHour

from core.utils import get_user_shop
from sales.models import Sale, SaleItem
from inventory.models import Product


def dashboard_view(request):

    shop = get_user_shop(request.user)

    today = date.today()

    # Base queryset (shop + today)
    sales_today = Sale.objects.filter(
        shop=shop,
        created_at__date=today
    )

    # Total number of transactions
    total_sales_count = sales_today.count()

    # TOTAL REVENUE (DB-level aggregation)
    total_revenue = SaleItem.objects.filter(
        sale__shop=shop,
        sale__created_at__date=today
    ).aggregate(
        total=Sum(F('quantity') * F('selling_price'))
    )['total'] or 0

    # TOTAL PROFIT (DB-level aggregation)
    total_profit = SaleItem.objects.filter(
        sale__shop=shop,
        sale__created_at__date=today
    ).aggregate(
        profit=Sum(
            ExpressionWrapper(
                (F('selling_price') - F('product__buying_price')) * F('quantity'),
                output_field=DecimalField()
            )
        )
    )['profit'] or 0

    # CREDIT SALES TOTAL
    total_credit = SaleItem.objects.filter(
        sale__shop=shop,
        sale__created_at__date=today,
        sale__payment_method='CREDIT'
    ).aggregate(
        total=Sum(F('quantity') * F('selling_price'))
    )['total'] or 0

    # LOW STOCK PRODUCTS
    low_stock_products = Product.objects.filter(
        shop=shop,
        stock_quantity__lte=5
    )

    # Top Selling Products
    top_products = SaleItem.objects.filter(
        sale__shop=shop,
        sale__created_at__date=today
    ).values(
        'product__name'
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('selling_price'))
    ).order_by('-total_qty')[:5]

    # Top Customers Today
    top_customers = Sale.objects.filter(
        shop=shop,
        created_at__date=today,
        customer__isnull=False
    ).values(
        'customer__name'
    ).annotate(
        total_spent=Sum(F('items__quantity') * F('items__selling_price'))
    ).order_by('-total_spent')[:5]

    # Hourly Sales Trend — simple version
    hourly_sales = Sale.objects.filter(
        shop=shop,
        created_at__date=today
    ).annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(
        total=Count('id')
    ).order_by('hour')

    context = {
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_credit': total_credit,
        'low_stock_products': low_stock_products,
    }

    context.update({
        'top_products': top_products,
        'top_customers': top_customers,
        'hourly_sales': hourly_sales,
    })

    return render(request, 'dashboard/dashboard.html', context)
