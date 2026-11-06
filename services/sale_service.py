from django.db import transaction
from django.core.exceptions import ValidationError
from sales.models import Sale, SaleItem
from inventory.models import Product, StockMovement


ALLOWED_PAYMENT_METHODS = {"CASH", "MOBILE", "CREDIT"}


class SaleService:

    @staticmethod
    @transaction.atomic
    def create_sale(*, shop, customer, payment_method, cart, shift=None, user=None):

        if payment_method not in ALLOWED_PAYMENT_METHODS:
            raise ValidationError(
                "Please choose a valid payment method."
            )

        if payment_method == "CREDIT" and customer is None:
            raise ValidationError(
                "Please select a customer for a credit sale."
            )

        if customer and customer.shop != shop:
            raise ValidationError(
                "Customer does not belong to this shop."
            )

        products = {}

        for product_id, item in cart.items():
            product = Product.objects.select_for_update().get(
                id=product_id,
                shop=shop
            )

            qty = item["qty"]

            if qty > product.stock_quantity:
                raise ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock_quantity}, Requested: {qty}"
                )

            products[product_id] = product


        sale = Sale.objects.create(
            shop=shop,
            customer=customer,
            payment_method=payment_method,
            shift=shift,
            created_by=user
        )

        for product_id, item in cart.items():
            product = products[product_id]
            qty = item["qty"]

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=qty,
                selling_price=item["price"]
            )

            StockMovement.objects.create(
                shop=shop,
                product=product,
                movement_type='OUT',
                quantity=qty,
                note=f"Sale {sale.receipt_number}"
            )

        return sale