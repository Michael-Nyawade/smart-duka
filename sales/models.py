from django.db import models
from inventory.models import Product, StockMovement
import uuid

class Customer(models.Model):
    name = models.CharField(max_length=100)

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

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
    
    def generate_receipt_number(self):
        return uuid.uuid4().hex[:10].upper()
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            while True:
                self.receipt_number = self.generate_receipt_number()
                if not Sale.objects.filter(receipt_number=self.receipt_number).exists():
                    break

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
