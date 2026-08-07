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
    help = "Seed SmartDuka multi-shop test data"

    def handle(self, *args, **kwargs):

        self.stdout.write("Resetting database...")

        self.clear_data()

        categories = self.create_categories()

        shop_a, users_a = self.create_shop(
            "SmartDuka Downtown",
            "Downtown Owner"
        )

        shop_b, users_b = self.create_shop(
            "SmartDuka Riverside",
            "Riverside Owner"
        )

        for shop, users in [
            (shop_a, users_a),
            (shop_b, users_b),
        ]:

            products = self.create_products(
                shop,
                categories
            )

            self.create_initial_stock(
                shop,
                products
            )

            self.create_customers(shop)

            shifts = self.create_shifts(users)

            self.create_sales(
                shop,
                users,
                products,
                shifts
            )


        self.stdout.write(
            self.style.SUCCESS(
                "SmartDuka seed completed"
            )
        )


    # -------------------------
    # RESET
    # -------------------------

    def clear_data(self):

        CreditPayment.objects.all().delete()
        Sale.objects.all().delete()
        StockMovement.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Customer.objects.all().delete()
        CashierShift.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        Shop.objects.all().delete()


    # -------------------------
    # SHOP + USERS
    # -------------------------

    def create_shop(self, name, owner):

        shop = Shop.objects.create(
            name=name,
            owner_name=owner
        )

        username = name.lower().replace(" ", "_")

        users = {}

        users["admin"] = User.objects.create_superuser(
            username=f"{username}_admin",
            email=f"{username}@smartduka.com",
            password="admin123"
        )

        users["manager"] = User.objects.create_user(
            username=f"{username}_manager",
            password="admin123"
        )

        users["cashier"] = User.objects.create_user(
            username=f"{username}_cashier",
            password="admin123"
        )


        roles = {
            "manager": "MANAGER",
            "cashier": "CASHIER",
        }


        for key, user in users.items():

            profile, _ = UserProfile.objects.get_or_create(
                user=user
            )

            profile.shop = shop

            if key in roles:
                profile.role = roles[key]

            else:
                profile.role = "ADMIN"

            profile.save()


        return shop, users


    # -------------------------
    # CATEGORIES
    # -------------------------

    def create_categories(self):

        names = [
            "Beverages",
            "Snacks",
            "Dairy",
            "Bread",
            "Oil",
            "Rice",
            "Sugar",
            "Soap",
            "Cosmetics",
            "Stationery",
        ]

        return [
            Category.objects.get_or_create(name=n)[0]
            for n in names
        ]


    # -------------------------
    # PRODUCTS
    # -------------------------

    def create_products(
        self,
        shop,
        categories
    ):

        products = []

        for i in range(50):

            category = random.choice(categories)

            buying = random.randint(
                20,
                500
            )

            product = Product.objects.create(
                shop=shop,
                category=category,
                name=f"{shop.name} Product {i}",
                sku=f"{shop.name[:3].upper()}-{random.randint(100000,999999)}-{i}",
                buying_price=buying,
                selling_price=buying + random.randint(5,100),
                stock_quantity=0,
                low_stock_threshold=10,
                reorder_level=20,
            )

            products.append(product)


        return products


    # -------------------------
    # STOCK
    # -------------------------

    def create_initial_stock(
        self,
        shop,
        products
    ):

        for product in products:

            StockMovement.objects.create(
                shop=shop,
                product=product,
                movement_type="IN",
                quantity=random.randint(50,200),
                note="Initial stock"
            )


    # -------------------------
    # CUSTOMERS
    # -------------------------

    def create_customers(self, shop):

        for i in range(10):

            Customer.objects.create(
                shop=shop,
                name=f"{shop.name} Customer {i}",
                phone_number=f"07000000{i}"
            )


    # -------------------------
    # SHIFTS
    # -------------------------

    def create_shifts(self, users):

        shifts=[]

        for user in users.values():

            shifts.append(
                CashierShift.objects.create(
                    user=user,
                    opening_cash=1000,
                    closed_at=timezone.now(),
                    is_active=False
                )
            )

        return shifts


    # -------------------------
    # SALES
    # -------------------------

    def create_sales(
        self,
        shop,
        users,
        products,
        shifts
    ):

        customers=list(
            Customer.objects.filter(shop=shop)
        )


        for day in range(30):

            sale_date = (
                timezone.now()
                -
                timedelta(days=day)
            )


            for _ in range(5):

                user=random.choice(
                    list(users.values())
                )

                shift=random.choice(shifts)

                customer=(
                    random.choice(customers)
                    if random.random() < 0.3
                    else None
                )


                product=random.choice(products)


                cart={
                    str(product.id):{
                        "qty":random.randint(1,3),
                        "price":float(
                            product.selling_price
                        )
                    }
                }


                payment=random.choice(
                    [
                        "CASH",
                        "MOBILE",
                        "CREDIT"
                    ]
                )


                sale=SaleService.create_sale(
                    shop=shop,
                    customer=customer,
                    payment_method=payment,
                    cart=cart,
                    shift=shift,
                    user=user
                )


                sale.created_at=sale_date
                sale.save(
                    update_fields=[
                        "created_at"
                    ]
                )


                StockMovement.objects.filter(
                    note=f"Sale {sale.receipt_number}"
                ).update(
                    created_at=sale_date
                )


                if payment=="CREDIT" and customer:

                    CreditPayment.objects.create(
                        customer=customer,
                        amount=random.randint(
                            100,
                            500
                        ),
                        notes="Payment"
                    )