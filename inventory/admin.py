from django.contrib import admin
from .models import Category, Product

# Register models
admin.site.register(Category)
admin.site.register(Product)