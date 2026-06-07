from django.db.models.signals import post_save
from django.dispatch import receiver

from sales.models import Sale, AuditLog
from core.audit import log_action


@receiver(post_save, sender=Sale)
def log_sale_created(sender, instance, created, **kwargs):

    if created:
        log_action(
            user=instance.created_by if hasattr(instance, "created_by") else None,
            action=f"Sale created: {instance.receipt_number}"
        )