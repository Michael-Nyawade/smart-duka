from django.db import transaction
from sales.models import Sale, SaleItem
from inventory.models import Product
from services.stock_service import StockService


class SaleService:

    @staticmethod
    @transaction.atomic
    def create_sale(*, shop, customer, payment_method, cart, shift=None, user=None):
        """
        Centralized sale creation logic.
        """

        sale = Sale.objects.create(
            shop=shop,
            customer=customer,
            payment_method=payment_method,
            shift=shift,
            created_by=user
        )

        for product_id, item in cart.items():

            product = Product.objects.select_for_update().get(
                id=product_id
            )

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=item["qty"],
                selling_price=item["price"]
            )

            # STOCK UPDATE THROUGH SERVICE
            StockService.decrease_stock(
                product=product,
                quantity=item["qty"],
                note=f"Sale {sale.receipt_number}"
            )

        return sale