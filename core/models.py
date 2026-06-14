from django.db import models
from django.contrib.auth.models import User

class Shop(models.Model):

    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):

    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("MANAGER", "Manager"),
        ("CASHIER", "Cashier"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="CASHIER"
    )

    def __str__(self):
        return self.user.username