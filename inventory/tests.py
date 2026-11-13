from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Shop
from inventory.models import Category, Product


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