from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import SaleItem
from inventory.models import StockMovement


@receiver(pre_delete, sender=SaleItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    StockMovement.objects.create(
        shop=instance.sale.shop,   # Enforce shop assignment
        product=instance.product,
        movement_type='IN',
        quantity=instance.quantity,
        note=f'Sale item deleted from receipt {instance.sale.receipt_number}'
    )
