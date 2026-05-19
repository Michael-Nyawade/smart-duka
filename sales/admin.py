from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = (
        'product',
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
