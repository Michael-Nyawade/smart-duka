from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.db import transaction
import uuid
from inventory.models import Product
from sales.models import Customer, Sale, SaleItem, CashierShift, AuditLog
from django.contrib.auth.decorators import login_required


@login_required
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


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('pos_home')

    customers = Customer.objects.all()
    total = sum(item['qty'] * item['price'] for item in cart.values())

    # Generate session lock token
    request.session['checkout_token'] = str(uuid.uuid4())

    return render(request, 'pos/checkout.html', {
        'cart': cart,
        'customers': customers,
        'total': total,
        'token': request.session['checkout_token']
    })


@login_required
@require_POST
@transaction.atomic
def process_checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('pos_home')

    # Validate session lock token
    token = request.POST.get('token')
    session_token = request.session.get('checkout_token')

    if not token or token != session_token:
        return redirect('pos_home')

    customer_id = request.POST.get('customer')
    payment_method = request.POST.get('payment_method')

    customer = None
    if customer_id:
        customer = Customer.objects.get(id=customer_id)

    # Get active cashier shift for this user
    shift_id = request.session.get("shift_id")
    shift = None
    if shift_id:
        shift = CashierShift.objects.filter(id=shift_id, is_active=True).first()

    # Restrict role: prevent Cashier from deleting or restricted actions
    if request.user.groups.filter(name="Cashier").exists() and payment_method == "DELETE":
        return HttpResponseForbidden("Not allowed")

    # LOCKED TRANSACTION
    sale = Sale.objects.create(
        customer=customer,
        payment_method=payment_method,
        shift=shift,
        created_by=request.user
    )

    for product_id, item in cart.items():
        product = Product.objects.select_for_update().get(id=product_id)
        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=item['qty'],
            selling_price=item['price']
        )

    # Audit log entry
    AuditLog.objects.create(
        user=request.user,
        action=f"Created sale {sale.receipt_number}"
    )

    # Clear cart and reset token
    request.session['cart'] = {}
    request.session['checkout_token'] = None

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

    html = render_to_string(
        "pos/cart_partial.html",
        {"cart": cart, "total": total},
        request=request
    )

    return JsonResponse({
        "cart_html": html,
        "total": total
    })


def api_update_cart(request):
    product_id = request.POST.get('product_id')
    action = request.POST.get('action')

    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid not in cart:
        return JsonResponse({'error': 'Item not in cart'})

    if action == "increase":
        cart[pid]['qty'] += 1
    elif action == "decrease":
        cart[pid]['qty'] -= 1
        if cart[pid]['qty'] <= 0:
            del cart[pid]

    request.session['cart'] = cart
    total = sum(item['qty'] * item['price'] for item in cart.values())

    html = render_to_string(
        "pos/cart_partial.html",
        {"cart": cart, "total": total},
        request=request
    )

    return JsonResponse({
        "cart_html": html,
        "total": total
    })
