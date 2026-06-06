from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import UserProfile, Shop


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        shop, _ = Shop.objects.get_or_create(
            name=f"{instance.username}'s Shop",
            defaults={"owner_name": instance.username}
        )

        UserProfile.objects.get_or_create(
            user=instance,
            defaults={"shop": shop}
        )