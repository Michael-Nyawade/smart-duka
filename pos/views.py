from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from inventory.models import Product
from sales.models import (
    Customer,
    CashierShift,
    AuditLog
)

from services.sale_service import SaleService

from core.utils import get_user_shop, for_current_shop


@login_required
def pos_home(request):
    products = for_current_shop(Product.objects.all(), request.user)
    cart = request.session.get("cart", {})

    total = sum(item["qty"] * item["price"] for item in cart.values())

    return render(request, "pos/pos_home.html", {
        "products": products,
        "cart": cart,
        "total": total,
    })


# HTMX checkout form endpoint
@login_required
def htmx_checkout_form(request):
    cart = request.session.get("cart", {})

    if not cart:
        return HttpResponse("Cart is empty")

    customers = Customer.objects.all()
    total = sum(i["qty"] * i["price"] for i in cart.values())

    return render(request, "pos/partials/checkout_form.html", {
        "cart": cart,
        "customers": customers,
        "total": total
    })


# HTMX checkout submission endpoint
@login_required
@require_POST
@transaction.atomic
def htmx_process_checkout(request):
    try:
        cart = request.session.get("cart", {})

        if not cart:
            return HttpResponseBadRequest("Cart is empty")

        customer_id = request.POST.get("customer")
        payment_method = request.POST.get("payment_method")

        customer = Customer.objects.filter(id=customer_id).first() if customer_id else None

        shift_id = request.session.get("shift_id")
        shift = CashierShift.objects.filter(id=shift_id, is_active=True).first()

        shop = get_user_shop(request.user)

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

        request.session["cart"] = {}

        return render(request, "pos/partials/receipt.html", {
            "sale": sale
        })

    except Exception as e:
        return render(request, "pos/partials/checkout_form.html", {
            "cart": cart,
            "customers": Customer.objects.all(),
            "total": sum(i["qty"] * i["price"] for i in cart.values()),
            "error": str(e),
        })


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


# HTMX cart endpoint
@login_required
@require_POST
def htmx_add_to_cart(request):
    from inventory.models import Product

    product_id = request.POST.get("product_id")
    product = Product.objects.get(id=product_id)

    cart = request.session.get("cart", {})
    pid = str(product_id)

    if pid in cart:
        cart[pid]["qty"] += 1
    else:
        cart[pid] = {
            "name": product.name,
            "qty": 1,
            "price": float(product.selling_price),
        }

    request.session["cart"] = cart

    total = sum(i["qty"] * i["price"] for i in cart.values())

    return render(request, "pos/partials/cart.html", {
        "cart": cart,
        "total": total,
    })
