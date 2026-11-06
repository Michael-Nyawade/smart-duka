from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from core.models import Shop
from inventory.models import Category, Product
from sales.models import Customer, Sale, SaleItem


class TenantIsolationTestCase(TestCase):
    """
    Regression tests ensuring a user from one shop can never view or modify
    another shop's data - even by directly manipulating a URL or ID.

    Also locks in the ADMIN/CASHIER role-matrix rules fixed previously,
    so a future change can't silently reintroduce that bug.
    """

    @classmethod
    def setUpTestData(cls):
        cls.shop_a = Shop.objects.create(name="Shop A", owner_name="Alice")
        cls.shop_b = Shop.objects.create(name="Shop B", owner_name="Bob")

        cls.admin_a = cls._make_user("admin_a", cls.shop_a, "ADMIN")
        cls.admin_b = cls._make_user("admin_b", cls.shop_b, "ADMIN")
        cls.cashier_a = cls._make_user("cashier_a", cls.shop_a, "CASHIER")

        # Category has no shop field in this app - it's shared globally.
        cls.category = Category.objects.create(name="General")

        cls.product_a = Product.objects.create(
            shop=cls.shop_a,
            category=cls.category,
            name="Shop A Product",
            sku="SHOPA-0001",
            buying_price=100,
            selling_price=150,
            stock_quantity=50,
        )
        cls.product_b = Product.objects.create(
            shop=cls.shop_b,
            category=cls.category,
            name="Shop B Product",
            sku="SHOPB-0001",
            buying_price=100,
            selling_price=150,
            stock_quantity=50,
        )

        cls.customer_a = Customer.objects.create(shop=cls.shop_a, name="Customer A")
        cls.customer_b = Customer.objects.create(shop=cls.shop_b, name="Customer B")

        cls.sale_a = Sale.objects.create(
            shop=cls.shop_a,
            customer=cls.customer_a,
            payment_method="CASH",
        )
        SaleItem.objects.create(
            sale=cls.sale_a,
            product=cls.product_a,
            quantity=1,
            selling_price=cls.product_a.selling_price,
        )

        cls.sale_b = Sale.objects.create(
            shop=cls.shop_b,
            customer=cls.customer_b,
            payment_method="CASH",
        )
        SaleItem.objects.create(
            sale=cls.sale_b,
            product=cls.product_b,
            quantity=1,
            selling_price=cls.product_b.selling_price,
        )

    @staticmethod
    def _make_user(username, shop, role):
        user = User.objects.create_user(username=username, password="testpass123!")
        # A UserProfile is auto-created by a post_save signal on User creation.
        user.userprofile.shop = shop
        user.userprofile.role = role
        user.userprofile.save()
        return user

    # --- Inventory ---

    def test_product_list_only_shows_own_shops_products(self):
        self.client.force_login(self.admin_a)
        response = self.client.get(reverse("product_list"))

        self.assertContains(response, self.product_a.name)
        self.assertNotContains(response, self.product_b.name)

    def test_cannot_view_another_shops_product_edit_form(self):
        self.client.force_login(self.admin_a)
        url = reverse("product_update", args=[self.product_b.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_cannot_submit_edits_to_another_shops_product(self):
        self.client.force_login(self.admin_a)
        url = reverse("product_update", args=[self.product_b.pk])

        response = self.client.post(url, {
            "category": self.category.pk,
            "name": "Hacked Name",
            "sku": self.product_b.sku,
            "buying_price": "1",
            "selling_price": "999999",
            "stock_quantity": "0",
        })

        self.assertEqual(response.status_code, 404)

        self.product_b.refresh_from_db()
        self.assertEqual(self.product_b.name, "Shop B Product")

    # --- Sales / customers ---

    def test_cannot_view_another_shops_customer(self):
        self.client.force_login(self.admin_a)
        url = reverse("customer_detail", args=[self.customer_b.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_cannot_add_payment_to_another_shops_customer(self):
        self.client.force_login(self.admin_a)
        url = reverse("add_payment", args=[self.customer_b.pk])

        response = self.client.post(url, {"amount": "500"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.customer_b.credit_payments.count(), 0)

    def test_cannot_view_another_shops_receipt(self):
        self.client.force_login(self.admin_a)
        url = reverse("sale-receipt", args=[self.sale_b.receipt_number])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_can_view_own_shops_receipt(self):
        self.client.force_login(self.admin_a)
        url = reverse("sale-receipt", args=[self.sale_a.receipt_number])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    # --- POS ---

    def test_cannot_add_another_shops_product_to_cart(self):
        self.client.force_login(self.admin_a)
        url = reverse("htmx_add_to_cart")

        response = self.client.post(url, {"product_id": self.product_b.pk})

        self.assertEqual(response.status_code, 404)

    def test_can_add_own_shops_product_to_cart(self):
        self.client.force_login(self.admin_a)
        url = reverse("htmx_add_to_cart")

        response = self.client.post(url, {"product_id": self.product_a.pk})

        self.assertEqual(response.status_code, 200)

    # --- Role matrix ---

    def test_admin_can_access_pos(self):
        self.client.force_login(self.admin_a)
        response = self.client.get(reverse("pos_home"))

        self.assertEqual(response.status_code, 200)

    def test_cashier_cannot_access_inventory(self):
        self.client.force_login(self.cashier_a)
        response = self.client.get(reverse("product_list"))

        self.assertEqual(response.status_code, 403)