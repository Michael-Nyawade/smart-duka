from django.shortcuts import render, redirect, get_object_or_404
from inventory.models import Product


def pos_home(request):

    products = Product.objects.all()

    cart = request.session.get('cart', {})

    if request.method == 'POST':

        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)

        if product_id in cart:
            cart[product_id]['qty'] += quantity
        else:
            cart[product_id] = {
                'name': product.name,
                'qty': quantity,
                'price': float(product.selling_price),
            }

        request.session['cart'] = cart

        return redirect('pos_home')

    # calculate total
    total = sum(item['qty'] * item['price'] for item in cart.values())

    context = {
        'products': products,
        'cart': cart,
        'total': total,
    }

    return render(request, 'pos/pos_home.html', context)