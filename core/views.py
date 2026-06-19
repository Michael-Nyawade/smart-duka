from datetime import date, timedelta

from django.shortcuts import render
from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField, Max
from django.db.models.functions import ExtractHour
from django.utils import timezone

from core.utils import get_user_shop
from sales.models import Sale, SaleItem, Customer
from inventory.models import Product
from inventory.services import InventoryIntelligence

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from core.decorators import allowed_roles


@login_required
@allowed_roles(["ADMIN", "MANAGER"])
def dashboard_view(request):
    shop = get_user_shop(request.user)
    today = date.today()

    # Base queryset (shop + today)
    sales_today = Sale.objects.filter(shop=shop, created_at__date=today)

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

    # CASH SALES TODAY
    cash_sales = SaleItem.objects.filter(
        sale__shop=shop,
        sale__created_at__date=today,
        sale__payment_method='CASH'
    ).aggregate(
        total=Sum(F('quantity') * F('selling_price'))
    )['total'] or 0

    # MOBILE MONEY SALES TODAY
    mobile_sales = SaleItem.objects.filter(
        sale__shop=shop,
        sale__created_at__date=today,
        sale__payment_method='MOBILE'
    ).aggregate(
        total=Sum(F('quantity') * F('selling_price'))
    )['total'] or 0

    # TOTAL CASH COLLECTED (REAL MONEY IN HAND)
    cash_collected = cash_sales + mobile_sales

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
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    dead_stock_products = Product.objects.filter(shop=shop).annotate(
        last_sold=Max('saleitem__sale__created_at')
    ).filter(
        last_sold__isnull=True
    ) | Product.objects.filter(shop=shop).annotate(
        last_sold=Max('saleitem__sale__created_at')
    ).filter(
        last_sold__lt=thirty_days_ago
    )

    # TOTAL OUTSTANDING CREDIT
    total_outstanding_credit = sum(
        customer.outstanding_balance()
        for customer in Customer.objects.filter(shop=shop)
    )

    # CREDIT AGING BUCKETS
    credit_sales = Sale.objects.filter(shop=shop, payment_method='CREDIT')

    total_credit_sales = credit_sales.aggregate(
        total=Sum(F("items__quantity") * F("items__selling_price"))
    )["total"] or 0

    total_outstanding_credit = sum(
        c.outstanding_balance()
        for c in Customer.objects.filter(shop=shop)
    )

    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    credit_0_7 = sum(
        s.total_amount()
        for s in credit_sales.filter(created_at__gte=seven_days_ago)
    )

    credit_8_30 = sum(
        s.total_amount()
        for s in credit_sales.filter(
            created_at__lt=seven_days_ago,
            created_at__gte=thirty_days_ago
        )
    )

    credit_30_plus = sum(
        s.total_amount()
        for s in credit_sales.filter(created_at__lt=thirty_days_ago)
    )

    context = {
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'expected_profit': expected_profit,
        'realized_profit': realized_profit,
        'total_credit': total_credit,
        'cash_sales': cash_sales,
        'mobile_sales': mobile_sales,
        'cash_collected': cash_collected,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'reorder_suggestions': reorder_suggestions,
        'total_outstanding_credit': total_outstanding_credit,
        'credit_0_7': credit_0_7,
        'credit_8_30': credit_8_30,
        'credit_30_plus': credit_30_plus,
        'total_credit_sales': total_credit_sales,
    }

    context.update({
        'top_products': top_products,
        'top_customers': top_customers,
        'hourly_sales': hourly_sales,
        'dead_stock_products': dead_stock_products,
    })

    return render(request, 'dashboard/dashboard.html', context)


@login_required
@allowed_roles(["ADMIN", "MANAGER"])
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


def _redirect_by_role(user):
    if user.is_superuser:
        return redirect("/admin/")

    role = getattr(user.userprofile, "role", None)

    if role == "CASHIER":
        return redirect("pos_home")

    if role == "MANAGER":
        return redirect("dashboard")

    return redirect("dashboard")


# POS Login View
def pos_login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # redirect based on role
            if user.is_superuser:
                return redirect("/admin/")

            role = getattr(user.userprofile, "role", None)

            if role == "CASHIER":
                return redirect("pos_home")

            if role == "MANAGER":
                return redirect("dashboard")

            return redirect("dashboard")

        error = "Invalid username or password"
    
    return render(request, "auth/login.html", {"error": error})

# Landing page view
def landing_page(request):
    return render(request, "landing.html")