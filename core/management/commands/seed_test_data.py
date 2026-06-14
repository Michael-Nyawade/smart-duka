from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random

from core.models import Shop, UserProfile
from inventory.models import Category, Product, StockMovement
from sales.models import Customer, CreditPayment, CashierShift, Sale
from services.sale_service import SaleService


class Command(BaseCommand):
    help = "Seed SmartDuka test data (FULL RESET MODE)"

    def handle(self, *args, **kwargs):
        self.stdout.write("Resetting database...")

        self.clear_data()
        shop, users = self.create_shop_and_users()
        categories = self.create_categories()
        products = self.create_products(shop, categories)
        self.create_initial_stock(shop, products)
        self.create_customers(shop)
        shifts = self.create_shifts(users)
        self.create_sales(shop, users, products, shifts)

        self.stdout.write(self.style.SUCCESS("SmartDuka seed completed successfully"))

    # ---------------------------
    # RESET
    # ---------------------------
    def clear_data(self):
        CreditPayment.objects.all().delete()
        Sale.objects.all().delete()
        StockMovement.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Customer.objects.all().delete()
        CashierShift.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        Shop.objects.all().delete()

    # ---------------------------
    # SHOP + USERS
    # ---------------------------
    def create_shop_and_users(self):
        shop = Shop.objects.create(
            name="SmartDuka Demo Shop",
            owner_name="Admin"
        )

        users = {}

        users["admin"] = User.objects.create_superuser(
            username="admin",
            email="admin@smartduka.com",
            password="admin123"
        )
        users["manager"] = User.objects.create_user("manager", password="admin123")
        users["cashier1"] = User.objects.create_user("cashier1", password="admin123")
        users["cashier2"] = User.objects.create_user("cashier2", password="admin123")

        # override signal-created profiles
        for u in users.values():
            profile = UserProfile.objects.get(user=u)
            profile.shop = shop
            profile.save()

        # assign roles
        UserProfile.objects.filter(user=users["manager"]).update(role="MANAGER")
        UserProfile.objects.filter(user=users["cashier1"]).update(role="CASHIER")
        UserProfile.objects.filter(user=users["cashier2"]).update(role="CASHIER")

        return shop, users

    # ---------------------------
    # CATEGORIES
    # ---------------------------
    def create_categories(self):
        names = [
            "Beverages", "Snacks", "Dairy", "Bread",
            "Cooking Oil", "Rice", "Sugar", "Soap",
            "Cosmetics", "Stationery"
        ]
        return [Category.objects.create(name=n) for n in names]

    # ---------------------------
    # PRODUCTS
    # ---------------------------
    def create_products(self, shop, categories):
        products = []

        for i in range(150):
            cat = random.choice(categories)

            buying = random.randint(20, 500)
            selling = buying + random.randint(5, 200)

            p = Product.objects.create(
                shop=shop,
                category=cat,
                name=f"{cat.name} Product {i}",
                sku=f"SKU-{i:04d}",
                buying_price=buying,
                selling_price=selling,
                stock_quantity=0,
                low_stock_threshold=random.randint(5, 15),
                reorder_level=random.randint(20, 40),
            )
            products.append(p)

        return products

    # ---------------------------
    # INITIAL STOCK
    # ---------------------------
    def create_initial_stock(self, shop, products):
        for p in products:
            qty = random.randint(50, 300)

            StockMovement.objects.create(
                shop=shop,
                product=p,
                movement_type="IN",
                quantity=qty,
                note="Initial stock"
            )

    # ---------------------------
    # CUSTOMERS
    # ---------------------------
    def create_customers(self, shop):
        for i in range(25):
            Customer.objects.create(
                shop=shop,
                name=f"Customer {i}",
                phone_number=f"07{random.randint(10000000, 99999999)}"
            )

    # ---------------------------
    # CASHIER SHIFTS
    # ---------------------------
    def create_shifts(self, users):
        shifts = []
        for u in users.values():
            shift = CashierShift.objects.create(
                user=u,
                opening_cash=1000,
                is_active=False,
                closed_at=timezone.now()
            )
            shifts.append(shift)
        return shifts

    # ---------------------------
    # SALES GENERATION
    # ---------------------------
    def create_sales(self, shop, users, products, shifts):
        customers = list(Customer.objects.filter(shop=shop))

        payment_methods = ["CASH", "MOBILE", "CREDIT"]

        for day in range(60):
            sale_date = timezone.now() - timedelta(days=day)

            for _ in range(random.randint(5, 15)):
                user = random.choice(list(users.values()))
                shift = random.choice(shifts)
                customer = random.choice(customers) if random.random() < 0.3 else None

                cart = {}
                items_count = random.randint(1, 4)

                for _ in range(items_count):
                    p = random.choice(products)
                    cart[str(p.id)] = {
                        "qty": random.randint(1, 5),
                        "price": float(p.selling_price)
                    }

                payment = random.choices(
                    payment_methods,
                    weights=[50, 25, 25]
                )[0]

                sale = SaleService.create_sale(
                    shop=shop,
                    customer=customer,
                    payment_method=payment,
                    cart=cart,
                    shift=shift,
                    user=user
                )

                # -----------------------
                # BACKDATE SALE
                # -----------------------
                sale.created_at = sale_date
                sale.save(update_fields=["created_at"])

                # -----------------------
                # BACKDATE STOCK MOVEMENTS
                # -----------------------
                StockMovement.objects.filter(
                    note=f"Sale {sale.receipt_number}"
                ).update(created_at=sale_date)

                # -----------------------
                # CREDIT PAYMENTS
                # -----------------------
                if payment == "CREDIT" and customer:
                    if random.random() < 0.5:
                        CreditPayment.objects.create(
                            customer=customer,
                            amount=random.randint(100, 1000),
                            notes="Partial payment"
                        )
