from django.contrib import admin
from .models import Sale, Customer, CreditPayment, SaleItem
from .models import SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    inlines = [SaleItemInline]

    list_display = (
        'receipt_number',
        'customer',
        'payment_method',
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