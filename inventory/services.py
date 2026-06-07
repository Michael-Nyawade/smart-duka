from inventory.models import Product
from django.db import models

class InventoryIntelligence:

    @staticmethod
    def get_low_stock_products(shop=None):
        """
        Products below warning threshold
        """
        qs = Product.objects.all()

        if shop:
            qs = qs.filter(shop=shop)

        return qs.filter(
            stock_quantity__lte=models.F("low_stock_threshold"),
            stock_quantity__gt=0
        )

    @staticmethod
    def get_out_of_stock(shop=None):
        qs = Product.objects.all()

        if shop:
            qs = qs.filter(shop=shop)

        return qs.filter(stock_quantity__lte=0)

    @staticmethod
    def get_reorder_candidates(shop=None):
        """
        Critical stock items that should be reordered
        """
        qs = Product.objects.all()

        if shop:
            qs = qs.filter(shop=shop)

        return qs.filter(
            stock_quantity__lte=models.F("reorder_level")
        )