from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create production admin user"

    def handle(self, *args, **kwargs):

        username = "admin"
        email = "admin@smartduka.com"
        password = "ChangeThisPassword123!"

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    "Admin already exists"
                )
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created admin user: {user.username}"
            )
        )