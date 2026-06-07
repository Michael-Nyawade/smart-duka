from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from django.db import transaction
from django.contrib.auth.decorators import login_required

import uuid

from inventory.models import Product
from sales.models import (
    Customer,
    Sale,
    SaleItem,
    CashierShift,
    AuditLog
)

from core.utils import get_user_shop, for_current_shop


@login_required
def pos_home(request):
    products = for_current_shop(Product.objects.all(), request.user)
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        product_id = request.POST.get('product')
        product = get_object_or_404(Product, id=product_id)
        pid = str(product.id)

        if pid in cart:
            cart[pid]['qty'] += 1
        else:
            cart[pid] = {
                'name': product.name,
                'qty': 1,
                'price': float(product.selling_price),
            }

        request.session['cart'] = cart
        return redirect('pos_home')

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

    request.session['checkout_token'] = str(uuid.uuid4())

    return render(
        request,
        'pos/checkout.html',
        {
            'cart': cart,
            'customers': customers,
            'total': total,
            'token': request.session['checkout_token']
        }
    )


@login_required
@require_POST
@transaction.atomic
def process_checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('pos_home')

    token = request.POST.get('token')
    session_token = request.session.get('checkout_token')

    if not token or token != session_token:
        return redirect('pos_home')

    customer_id = request.POST.get('customer')
    payment_method = request.POST.get('payment_method')

    customer = None
    if customer_id:
        customer = Customer.objects.get(id=customer_id)

    shift_id = request.session.get("shift_id")
    shift = None
    if shift_id:
        shift = CashierShift.objects.filter(id=shift_id, is_active=True).first()

    shop = get_user_shop(request.user)

    from services.sale_service import SaleService
    sale = SaleService.create_sale(
        shop=shop,
        customer=customer,
        payment_method=payment_method,
        cart=cart,
        shift=shift,
        user=request.user
    )

    AuditLog.objects.create(
        user=request.user,
        action=f"Created sale {sale.receipt_number}"
    )

    request.session['cart'] = {}
    request.session['checkout_token'] = None

    return render(request, 'pos/receipt.html', {'sale': sale})


@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    request.session['cart'] = cart
    return redirect('pos_home')


@login_required
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('pos_home')


@login_required
def increase_qty(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        cart[pid]['qty'] += 1

    request.session['cart'] = cart
    return redirect('pos_home')


@login_required
def decrease_qty(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        cart[pid]['qty'] -= 1
        if cart[pid]['qty'] <= 0:
            del cart[pid]

    request.session['cart'] = cart
    return redirect('pos_home')


@login_required
@require_POST
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
        'pos/cart_partial.html',
        {'cart': cart, 'total': total},
        request=request
    )

    return JsonResponse({'cart_html': html, 'total': total})


@login_required
@require_POST
def api_update_cart(request):
    product_id = request.POST.get('product_id')
    action = request.POST.get('action')

    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid not in cart:
        return JsonResponse({'error': 'Item not in cart'}, status=400)

    if action == 'increase':
        cart[pid]['qty'] += 1
    elif action == 'decrease':
        cart[pid]['qty'] -= 1
        if cart[pid]['qty'] <= 0:
            del cart[pid]

    request.session['cart'] = cart
    total = sum(item['qty'] * item['price'] for item in cart.values())

    html = render_to_string(
        'pos/cart_partial.html',
        {'cart': cart, 'total': total},
        request=request
    )

    return JsonResponse({'cart_html': html, 'total': total})


@login_required
def pos_products_partial(request):
    shop = get_user_shop(request.user)
    products = Product.objects.filter(shop=shop)

    html = render_to_string('pos/partials/products.html', {'products': products})
    return HttpResponse(html)


@login_required
def pos_search_products(request):
    shop = get_user_shop(request.user)
    query = request.GET.get('q', '')

    products = Product.objects.filter(shop=shop, name__icontains=query)[:10]

    data = [
        {
            'id': p.id,
            'name': p.name,
            'price': str(p.selling_price),
            'stock': p.stock_quantity,
        }
        for p in products
    ]

    return JsonResponse(data, safe=False)


# Refund endpoint
@login_required
def refund_sale(request, sale_id):
    from services.refund_service import RefundService

    RefundService.refund_sale(
        sale_id=sale_id,
        user=request.user
    )

    return redirect('pos_home')
