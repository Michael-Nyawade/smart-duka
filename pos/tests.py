from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Shop
from inventory.models import Category, Product
from sales.models import Customer, Sale


class CheckoutFlowTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.shop = Shop.objects.create(name="Test Shop", owner_name="Owner")

        cls.user = User.objects.create_user(
            username="cashier",
            password="testpass123!",
        )
        cls.user.userprofile.shop = cls.shop
        cls.user.userprofile.role = "CASHIER"
        cls.user.userprofile.save()

        category = Category.objects.create(name="General")

        cls.product = Product.objects.create(
            shop=cls.shop,
            category=category,
            name="Test Product",
            sku="POS-0001",
            buying_price=100,
            selling_price=150,
            stock_quantity=10,
        )

        cls.customer = Customer.objects.create(
            shop=cls.shop,
            name="Test Customer",
        )

    def setUp(self):
        self.client.force_login(self.user)

        session = self.client.session
        session["cart"] = {
            str(self.product.pk): {
                "name": self.product.name,
                "qty": 1,
                "price": 150.0,
            }
        }
        session.save()

    def test_credit_checkout_without_customer_shows_error_and_keeps_choices(self):
        response = self.client.post(reverse("htmx_process_checkout"), {
            "customer": "",
            "payment_method": "CREDIT",
        })

        self.assertContains(response, "Please select a customer for a credit sale.")
        # The cashier's Credit choice must survive the error.
        self.assertContains(response, 'value="CREDIT" selected')
        # Nothing was sold and the cart is untouched.
        self.assertEqual(Sale.objects.count(), 0)
        self.assertTrue(self.client.session["cart"])

    def test_credit_checkout_with_customer_completes_and_clears_cart(self):
        response = self.client.post(reverse("htmx_process_checkout"), {
            "customer": str(self.customer.pk),
            "payment_method": "CREDIT",
        })

        self.assertContains(response, "Sale Completed")
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(self.client.session["cart"], {})