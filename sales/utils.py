from django.db.models import Sum, F, DecimalField
from django.utils import timezone

from .models import Sale


def get_today_sales():

    today = timezone.now().date()

    return Sale.objects.filter(
        created_at__date=today
    )


def get_daily_sales_summary():

    today_sales = get_today_sales()

    total_sales_count = today_sales.count()

    total_revenue = sum(
        sale.total_amount()
        for sale in today_sales
    )

    total_profit = sum(
        sale.profit()
        for sale in today_sales
    )

    credit_sales_count = today_sales.filter(
        payment_method='CREDIT'
    ).count()

    mobile_money_sales_count = today_sales.filter(
        payment_method='MOBILE'
    ).count()

    cash_sales_count = today_sales.filter(
        payment_method='CASH'
    ).count()

    return {
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'credit_sales_count': credit_sales_count,
        'mobile_money_sales_count': mobile_money_sales_count,
        'cash_sales_count': cash_sales_count,
    }