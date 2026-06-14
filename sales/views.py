from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.utils import get_user_shop
from .models import Sale, Customer, CreditPayment


@login_required
def sale_receipt_view(request, receipt_number):
    shop = get_user_shop(request.user)

    sale = get_object_or_404(
        Sale,
        receipt_number=receipt_number,
        shop=shop
    )

    context = {
        'sale': sale
    }

    return render(request, 'sales/receipt.html', context)


@login_required
def customer_detail(request, pk):
    shop = get_user_shop(request.user)

    customer = get_object_or_404(
        Customer,
        pk=pk,
        shop=shop
    )

    sales = customer.sales.all()
    payments = customer.credit_payments.all()

    context = {
        'customer': customer,
        'sales': sales,
        'payments': payments,
    }

    return render(request, 'sales/customer_detail.html', context)


@login_required
def add_payment(request, pk):
    shop = get_user_shop(request.user)

    customer = get_object_or_404(
        Customer,
        pk=pk,
        shop=shop
    )

    if request.method == "POST":
        amount = request.POST.get('amount')
        notes = request.POST.get('notes', '')

        CreditPayment.objects.create(
            customer=customer,
            amount=amount,
            notes=notes
        )

        return redirect('customer_detail', pk=customer.id)

    return render(request, 'sales/add_payment.html', {
        'customer': customer
    })
