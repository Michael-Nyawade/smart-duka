from django.test import TestCase

# Create your tests here.
from django.test import TestCase

from inventory.models import Category


class StarterCategoriesTests(TestCase):

    def test_starter_categories_exist_after_migrations(self):
        for name in ["Beverages", "Sugar", "Rice", "Other"]:
            self.assertTrue(
                Category.objects.filter(name=name).exists(),
                f"Missing starter category: {name}",
            )