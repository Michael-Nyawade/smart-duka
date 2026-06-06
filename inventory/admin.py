from django.contrib import admin
from .models import Category, Product, StockMovement
from core.utils import get_user_shop

# Register models
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'sku',
        'stock_quantity',
        'buying_price',
        'selling_price',
        'profit_per_item',
        'low_stock_status',
        'dead_stock_status',
    )

    list_filter = ('category',)
    search_fields = ('name', 'sku')

    # All stock changes happen through Stock Movements
    readonly_fields = ('stock_quantity',)

    list_per_page = 20
    ordering = ('name',) 

    def low_stock_status(self, obj):
        return obj.is_low_stock()

    low_stock_status.boolean = True
    low_stock_status.short_description = 'Low Stock'

    def dead_stock_status(self, obj):
        return obj.is_dead_stock()

    dead_stock_status.boolean = True
    dead_stock_status.short_description = 'Dead Stock'

    # Ensure new products are assigned to the current user's shop
    def save_model(self, request, obj, form, change):
        obj.shop = get_user_shop(request.user)
        super().save_model(request, obj, form, change)


@admin.register(StockMovement)
class StockMovement(admin.ModelAdmin):
    list_display = (
        'product',
        'movement_type',
        'quantity',
        'created_at',
    )

    list_filter = ('movement_type', 'created_at')
    search_fields = ('product__name',)
