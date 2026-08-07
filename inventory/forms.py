from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):

    initial_stock = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Initial Stock"
    )

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
            "initial_stock",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "sku": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "buying_price": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "selling_price": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "low_stock_threshold": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "reorder_level": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }