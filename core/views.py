from datetime import date, timedelta

from django.shortcuts import render
from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField, Max
from django.db.models.functions import ExtractHour
from django.utils import timezone

from core.utils import get_user_shop
from sales.models import Sale, SaleItem
from inventory.models import Product
from inventory.services import InventoryIntelligence


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

    # EXPECTED PROFIT
    expected_profit = SaleItem.objects.filter(
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

    # REALIZED PROFIT (only CASH + MOBILE)
    realized_profit = SaleItem.objects.filter(
        sale__shop=shop,
        sale__created_at__date=today,
        sale__payment_method__in=['CASH', 'MOBILE']
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
        stock_quantity__lte=F('low_stock_threshold')
    )

    # Reorder alerts count
    low_stock_count = low_stock_products.count()

    # Reorder suggestion logic
    reorder_suggestions = []
    for product in low_stock_products:
        suggested_qty = product.reorder_level * 2 - product.stock_quantity
        reorder_suggestions.append({
            'product': product,
            'suggested_qty': max(suggested_qty, 0)
        })

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

    # DEAD STOCK LOGIC
    thirty_days_ago = timezone.now() - timedelta(days=30)

    dead_stock_products = Product.objects.filter(
        shop=shop
    ).annotate(
        last_sold=Max('saleitem__sale__created_at')
    ).filter(
        last_sold__isnull=True
    ) | Product.objects.filter(
        shop=shop
    ).annotate(
        last_sold=Max('saleitem__sale__created_at')
    ).filter(
        last_sold__lt=thirty_days_ago
    )

    context = {
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'expected_profit': expected_profit,
        'realized_profit': realized_profit,
        'total_credit': total_credit,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'reorder_suggestions': reorder_suggestions,
    }

    context.update({
        'top_products': top_products,
        'top_customers': top_customers,
        'hourly_sales': hourly_sales,
        'dead_stock_products': dead_stock_products,
    })

    return render(request, 'dashboard/dashboard.html', context)


def inventory_alerts(request):

    shop = get_user_shop(request.user)

    low_stock = InventoryIntelligence.get_low_stock_products(shop)
    out_of_stock = InventoryIntelligence.get_out_of_stock(shop)
    reorder = InventoryIntelligence.get_reorder_candidates(shop)

    return render(request, "dashboard/inventory_alerts.html", {
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "reorder": reorder,
    })
