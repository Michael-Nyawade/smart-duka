from django.shortcuts import render
from inventory.models import Product

def pos_home(request):

    products = Product.objects.all()

    context = {
        'products': products
    }

    return render(request, 'pos/pos_home.html', context)