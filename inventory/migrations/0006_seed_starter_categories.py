from django.db import migrations

STARTER_CATEGORIES = [
    "Beverages",
    "Bread & Bakery",
    "Cosmetics",
    "Dairy",
    "Flour",
    "Fruits & Vegetables",
    "Household",
    "Oil",
    "Rice",
    "Snacks",
    "Soap",
    "Stationery",
    "Sugar",
    "Toiletries",
    "Other",
]


def add_starter_categories(apps, schema_editor):
    Category = apps.get_model("inventory", "Category")

    for name in STARTER_CATEGORIES:
        Category.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_product_reorder_level_and_more"),
    ]

    operations = [
        # Reverse is a no-op on purpose: never delete categories that
        # products may already be using.
        migrations.RunPython(add_starter_categories, migrations.RunPython.noop),
    ]