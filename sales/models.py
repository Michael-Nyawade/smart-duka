from django.db import models
from inventory.models import Product, StockMovement
import uuid
from django.conf import settings
from core.models import Shop
from core.managers import ShopQuerySet


class Customer(models.Model):
    name = models.CharField(max_length=100)

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        null=True
    )

    # Enforce shop isolation
    objects = ShopQuerySet.as_manager()

    def total_credit_sales(self):
        return sum(
            sale.total_amount()
            for sale in self.sales.filter(
                payment_method='CREDIT'
            )
        )

    def total_payments(self):
        return sum(
            payment.amount
            for payment in self.credit_payments.all()
        )

    def outstanding_balance(self):
        return (
            self.total_credit_sales()
            - self.total_payments()
        )

    def __str__(self):
        return self.name


class CreditPayment(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='credit_payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.customer.name} - {self.amount}"


class CashierShift(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    opening_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    closing_cash = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.opened_at}"


class Sale(models.Model):
    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('MOBILE', 'Mobile Money'),
        ('CREDIT', 'Credit'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales'
    )

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS
    )

    created_at = models.DateTimeField(auto_now_add=True)

    shift = models.ForeignKey(
        CashierShift,
        on_delete=models.SET_NULL,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales"
    )

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        null=True
    )

    # Enforce shop isolation
    objects = ShopQuerySet.as_manager()

    def generate_receipt_number(self):
        return uuid.uuid4().hex[:10].upper()

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def total_amount(self):
        return sum(item.total() for item in self.items.all())

    def profit(self):
        return sum(item.profit() for item in self.items.all())

    def __str__(self):
        return self.receipt_number or "Sale"


class SaleItem(models.Model):
    sale = models.ForeignKey(
        'Sale',
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def total(self):
        return self.quantity * self.selling_price

    def profit(self):
        return (
            self.selling_price - self.product.buying_price
        ) * self.quantity


    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
