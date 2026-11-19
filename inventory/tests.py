from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Shop
from inventory.models import Category, Product, StockMovement


class StarterCategoriesTests(TestCase):

    def test_starter_categories_exist_after_migrations(self):
        for name in ["Beverages", "Sugar", "Rice", "Other"]:
            self.assertTrue(
                Category.objects.filter(name=name).exists(),
                f"Missing starter category: {name}",
            )


class SkuPerShopTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.shop_a = Shop.objects.create(name="Shop A", owner_name="Alice")
        cls.shop_b = Shop.objects.create(name="Shop B", owner_name="Bob")

        cls.admin_a = cls._make_admin("sku_admin_a", cls.shop_a)
        cls.admin_b = cls._make_admin("sku_admin_b", cls.shop_b)

        cls.category, _ = Category.objects.get_or_create(name="Beverages")

    @staticmethod
    def _make_admin(username, shop):
        user = User.objects.create_user(username=username, password="testpass123!")
        user.userprofile.shop = shop
        user.userprofile.role = "ADMIN"
        user.userprofile.save()
        return user

    def _product_data(self, sku, name="Item"):
        return {
            "category": self.category.pk,
            "name": name,
            "sku": sku,
            "buying_price": "10",
            "selling_price": "15",
            "low_stock_threshold": "10",
            "reorder_level": "20",
        }

    def test_two_shops_can_use_the_same_sku(self):
        self.client.force_login(self.admin_a)
        first = self.client.post(reverse("product_create"), self._product_data("001"))

        self.client.force_login(self.admin_b)
        second = self.client.post(reverse("product_create"), self._product_data("001"))

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Product.objects.filter(sku="001").count(), 2)

    def test_same_shop_duplicate_sku_shows_form_error_not_a_crash(self):
        self.client.force_login(self.admin_a)

        self.client.post(reverse("product_create"), self._product_data("001"))
        response = self.client.post(reverse("product_create"), self._product_data("001"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists in your shop")
        self.assertEqual(Product.objects.filter(shop=self.shop_a, sku="001").count(), 1)

    def test_editing_a_product_with_its_own_sku_is_not_a_duplicate(self):
        self.client.force_login(self.admin_a)
        self.client.post(reverse("product_create"), self._product_data("001"))
        product = Product.objects.get(shop=self.shop_a, sku="001")

        response = self.client.post(
            reverse("product_update", args=[product.pk]),
            self._product_data("001", name="Renamed"),
        )

        self.assertEqual(response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.name, "Renamed")


class InventoryPagesRenderTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.shop = Shop.objects.create(name="Page Shop", owner_name="Owner")

        cls.user = User.objects.create_user(
            username="pages_admin",
            password="testpass123!",
        )
        cls.user.userprofile.shop = cls.shop
        cls.user.userprofile.role = "ADMIN"
        cls.user.userprofile.save()

        category, _ = Category.objects.get_or_create(name="Beverages")

        cls.product = Product.objects.create(
            shop=cls.shop,
            category=category,
            name="Page Product",
            sku="PG-001",
            buying_price=10,
            selling_price=15,
            stock_quantity=0,
        )
        cls.empty_product = Product.objects.create(
            shop=cls.shop,
            category=category,
            name="Empty Product",
            sku="PG-002",
            buying_price=10,
            selling_price=15,
            stock_quantity=0,
        )

        StockMovement.objects.create(
            shop=cls.shop,
            product=cls.product,
            movement_type="IN",
            quantity=2,
            note="Opening stock",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_product_list_renders(self):
        response = self.client.get(reverse("product_list"))
        self.assertContains(response, "Page Product")
        self.assertContains(response, "Out of stock")

    def test_product_forms_render(self):
        add = self.client.get(reverse("product_create"))
        self.assertContains(add, "Add Product")

        edit = self.client.get(reverse("product_update", args=[self.product.pk]))
        self.assertContains(edit, "Edit Product")
        self.assertContains(edit, "Page Product")

    def test_stock_receive_page_renders(self):
        response = self.client.get(reverse("stock_receive"))
        self.assertEqual(response.status_code, 200)

    def test_receiving_zero_quantity_is_rejected(self):
        response = self.client.post(reverse("stock_receive"), {
            "product": self.product.pk,
            "quantity": "0",
            "note": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least 1")

    def test_stock_history_renders(self):
        response = self.client.get(reverse("stock_movement_list"))
        self.assertContains(response, "Opening stock")

    def test_alerts_page_renders(self):
        response = self.client.get(reverse("inventory_alerts"))
        self.assertContains(response, "Empty Product")