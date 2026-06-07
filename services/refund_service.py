# services/refund_service.py

from django.db import transaction
from sales.models import Sale, SaleItem
from services.stock_service import StockService
from core.audit import log_action


class RefundService:

    @staticmethod
    @transaction.atomic
    def refund_sale(*, sale_id, user, partial_items=None):
        """
        Refund a full or partial sale.
        """

        sale = Sale.objects.select_for_update().get(id=sale_id)

        items = sale.items.all()

        # If partial refund is provided
        if partial_items:
            items = items.filter(id__in=partial_items)

        for item in items:
            StockService.reverse_decrease_stock(
                product=item.product,
                quantity=item.quantity,
                note=f"Refund for sale {sale.receipt_number}"
            )

        log_action(
            user=user,
            action=f"Refund processed for sale {sale.receipt_number}"
        )

        return sale
