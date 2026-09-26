from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = "Create production admin user (credentials come from environment variables)"

    def handle(self, *args, **kwargs):
        username = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
        email = os.environ.get("DJANGO_ADMIN_EMAIL", "admin@smartduka.com")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not password:
            raise CommandError(
                "DJANGO_ADMIN_PASSWORD environment variable is not set. "
                "Set it before running this command; no default password is provided."
            )

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING("Admin already exists")
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(f"Created admin user: {user.username}")
        )