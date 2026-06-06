from django.contrib import admin
from .models import Shop, UserProfile

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "shop")
    search_fields = ("user__username", "shop__name")
    list_filter = ("shop",)
