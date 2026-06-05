from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from inventory.models import Product
from sales.models import Customer, Sale, SaleItem


def pos_home(request):

    products = Product.objects.all()

    cart = request.session.get('cart', {})

    if request.method == 'POST':

        product_id = request.POST.get('product')

        product = get_object_or_404(Product, id=product_id)

        # Faster add-to-cart: always +1
        if product_id in cart:
            cart[product_id]['qty'] += 1
        else:
            cart[product_id] = {
                'name': product.name,
                'qty': 1,
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


def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('pos_home')

    customers = Customer.objects.all()

    total = sum(item['qty'] * item['price'] for item in cart.values())

    return render(request, 'pos/checkout.html', {
        'cart': cart,
        'customers': customers,
        'total': total
    })


@require_POST
def process_checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('pos_home')

    customer_id = request.POST.get('customer')
    payment_method = request.POST.get('payment_method')

    customer = None
    if customer_id:
        customer = Customer.objects.get(id=customer_id)

    # Create sale
    sale = Sale.objects.create(
        customer=customer,
        payment_method=payment_method
    )

    # Create items
    for product_id, item in cart.items():

        product = Product.objects.get(id=product_id)

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=item['qty'],
            selling_price=item['price']
        )

    # Clear cart
    request.session['cart'] = {}

    return render(request, 'pos/receipt.html', {
        'sale': sale
    })


def remove_from_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart

    return redirect('pos_home')


def clear_cart(request):

    request.session['cart'] = {}

    return redirect('pos_home')

def increase_qty(request, product_id):

    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        cart[pid]['qty'] += 1

    request.session['cart'] = cart
    return redirect('pos_home')


def decrease_qty(request, product_id):

    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        cart[pid]['qty'] -= 1

        if cart[pid]['qty'] <= 0:
            del cart[pid]

    request.session['cart'] = cart
    return redirect('pos_home')

def api_add_to_cart(request):

    product_id = request.POST.get('product_id')

    product = Product.objects.get(id=product_id)

    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        cart[pid]['qty'] += 1
    else:
        cart[pid] = {
            'name': product.name,
            'qty': 1,
            'price': float(product.selling_price),
        }

    request.session['cart'] = cart

    total = sum(item['qty'] * item['price'] for item in cart.values())

    return JsonResponse({
        'cart': cart,
        'total': total
    })
