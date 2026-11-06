from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import Shop
from inventory.models import Category, Product
from sales.models import Customer, Sale
from services.sale_service import SaleService


class SaleServicePaymentRulesTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.shop = Shop.objects.create(name="Test Shop", owner_name="Owner")
        category = Category.objects.create(name="General")

        cls.product = Product.objects.create(
            shop=cls.shop,
            category=category,
            name="Test Product",
            sku="TEST-0001",
            buying_price=100,
            selling_price=150,
            stock_quantity=10,
        )

        cls.customer = Customer.objects.create(
            shop=cls.shop,
            name="Test Customer",
        )

    def _cart(self, qty=1):
        return {
            str(self.product.pk): {
                "name": self.product.name,
                "qty": qty,
                "price": 150.0,
            }
        }

    def test_credit_sale_without_customer_is_rejected(self):
        with self.assertRaises(ValidationError):
            SaleService.create_sale(
                shop=self.shop,
                customer=None,
                payment_method="CREDIT",
                cart=self._cart(),
            )

        self.assertEqual(Sale.objects.count(), 0)

    def test_credit_sale_with_customer_succeeds(self):
        sale = SaleService.create_sale(
            shop=self.shop,
            customer=self.customer,
            payment_method="CREDIT",
            cart=self._cart(),
        )

        self.assertEqual(sale.payment_method, "CREDIT")
        self.assertEqual(sale.customer, self.customer)

    def test_cash_sale_without_customer_still_works(self):
        sale = SaleService.create_sale(
            shop=self.shop,
            customer=None,
            payment_method="CASH",
            cart=self._cart(),
        )

        self.assertEqual(sale.payment_method, "CASH")
        self.assertIsNone(sale.customer)

    def test_invalid_payment_method_is_rejected(self):
        with self.assertRaises(ValidationError):
            SaleService.create_sale(
                shop=self.shop,
                customer=None,
                payment_method="BARTER",
                cart=self._cart(),
            )

        self.assertEqual(Sale.objects.count(), 0)