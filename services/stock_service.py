from inventory.models import Product, StockMovement
from django.core.exceptions import ValidationError


class StockService:

    @staticmethod
    def decrease_stock(product, quantity, note="Sale"):
        """
        Reduce stock safely and record movement.
        """

        if product.stock_quantity < quantity:
            raise ValidationError("Not enough stock available.")

        product.stock_quantity -= quantity
        product.save()

        StockMovement.objects.create(
            product=product,
            movement_type="OUT",
            quantity=quantity,
            note=note
        )

    @staticmethod
    def increase_stock(product, quantity, note="Reversal"):
        """
        Increase stock (used for refunds/deletes).
        """

        product.stock_quantity += quantity
        product.save()

        StockMovement.objects.create(
            product=product,
            movement_type="IN",
            quantity=quantity,
            note=note
        )