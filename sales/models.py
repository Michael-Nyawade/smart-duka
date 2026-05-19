from django.db import models
from inventory.models import Product, StockMovement


class Sale(models.Model):

    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('MOBILE', 'Mobile Money'),
        ('CREDIT', 'Credit'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sales'
    )

    quantity = models.PositiveIntegerField()

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def total_amount(self):
        return self.quantity * self.selling_price

    def profit(self):
        return (
            self.selling_price - self.product.buying_price
        ) * self.quantity

    def save(self, *args, **kwargs):

        if not self.pk:

            StockMovement.objects.create(
                product=self.product,
                movement_type='OUT',
                quantity=self.quantity,
                note='Product sold'
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
