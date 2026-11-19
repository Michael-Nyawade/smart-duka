from django import forms
from .models import Product, StockMovement


def apply_input_styling(form):
    """Give every field the app's standard input styling."""
    for field in form.fields.values():
        if isinstance(field.widget, forms.Select):
            field.widget.attrs["class"] = "form-select"
        else:
            field.widget.attrs["class"] = "form-control"


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

    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop
        apply_input_styling(self)
        self.fields["sku"].widget.attrs["placeholder"] = "e.g. BEV001"

    def clean_sku(self):
        sku = self.cleaned_data["sku"].strip()

        # The shop isn't a form field, so Django's own uniqueness check
        # skips (shop, sku). Check it here against the current shop.
        if self.shop is not None:
            duplicates = Product.objects.filter(shop=self.shop, sku=sku)

            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)

            if duplicates.exists():
                raise forms.ValidationError(
                    "A product with this SKU already exists in your shop."
                )

        return sku


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

        apply_input_styling(self)
        self.fields["quantity"].widget.attrs["min"] = 1
        self.fields["note"].widget.attrs["rows"] = 3
        self.fields["note"].widget.attrs["placeholder"] = "e.g. Delivery from supplier"

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity < 1:
            raise forms.ValidationError("Enter a quantity of at least 1.")

        return quantity