from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ShopOwnerRegistrationForm(UserCreationForm):
    shop_name = forms.CharField(max_length=100)
    owner_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = [
            "username",
            "shop_name",
            "owner_name",
            "password1",
            "password2",
        ]