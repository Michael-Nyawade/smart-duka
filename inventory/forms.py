from django import forms
from .models import Product, StockMovement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "sku",
            "buying_price",
            "selling_price",
            "low_stock_threshold",
            "reorder_level",
        ]


class StockReceiveForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "product",
            "quantity",
            "note",
        ]

    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)

        if shop:
            self.fields["product"].queryset = Product.objects.filter(
                shop=shop
            )