from django.contrib import admin
from .models import Sale, Customer


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = (
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
        'created_at',
    )

    search_fields = (
        'name',
        'phone_number',
    )