from django.contrib import admin
from .models import Category, Product

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
    )

    list_filter = ('category',)
    search_fields = ('name', 'sku')

    def low_stock_status(self, obj):
        return obj.is_low_stock()

    low_stock_status.boolean = True
    low_stock_status.short_description = 'Low Stock'
