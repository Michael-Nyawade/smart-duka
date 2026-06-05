from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)  # Stock Keeping Unit

    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def profit_per_item(self):
        return self.selling_price - self.buying_price

    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    # Dead stock detection
    def is_dead_stock(self):

        latest_movement = self.stock_movements.order_by('-created_at').first()

        if not latest_movement:
            return True

        dead_stock_threshold = timezone.now() - timedelta(days=30)

        return latest_movement.created_at < dead_stock_threshold

    def __str__(self):
        return self.name


class StockMovement(models.Model):

    MOVEMENT_TYPES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements'
    )

    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_TYPES
    )

    quantity = models.PositiveIntegerField()

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Safe stock update with transaction and row-level locking
    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                product = Product.objects.select_for_update().get(pk=self.product.pk)

                if self.movement_type == 'OUT':
                    if product.stock_quantity < self.quantity:
                        raise ValueError("Insufficient stock")
                    product.stock_quantity -= self.quantity

                elif self.movement_type == 'IN':
                    product.stock_quantity += self.quantity

                product.save()

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"
