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

    readonly_fields = ('stock_quantity',)

    list_per_page = 20
    ordering = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            shop=get_user_shop(request.user)
        )

    def low_stock_status(self, obj):
        return obj.is_low_stock()

    low_stock_status.boolean = True
    low_stock_status.short_description = 'Low Stock'

    def dead_stock_status(self, obj):
        return obj.is_dead_stock()

    dead_stock_status.boolean = True
    dead_stock_status.short_description = 'Dead Stock'

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.shop = get_user_shop(request.user)

        super().save_model(request, obj, form, change)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'movement_type',
        'quantity',
        'created_at',
    )

    list_filter = (
        'movement_type',
        'created_at',
    )

    search_fields = (
        'product__name',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            shop=get_user_shop(request.user)
        )