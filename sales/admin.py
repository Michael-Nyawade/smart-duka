from django.contrib import admin
from .models import Sale, Customer, CreditPayment


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = (
        'receipt_number',
        'product',
        'customer',
        'quantity',
        'selling_price',
        'payment_method',
        'total_amount',
        'profit',
        'created_at',
    )

    list_filter = (
        'payment_method',
        'created_at',
    )

    search_fields = (
        'product__name',
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'phone_number',
        'total_credit_sales',
        'total_payments',
        'outstanding_balance',
        'created_at',
    )

    search_fields = (
        'name',
        'phone_number',
    )

@admin.register(CreditPayment)
class CreditPaymentAdmin(admin.ModelAdmin):

    list_display = (
        'customer',
        'amount',
        'created_at',
    )

    search_fields = (
        'customer__name',
    )