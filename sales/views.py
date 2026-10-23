from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.utils import get_user_shop
from .models import Sale, Customer, CreditPayment
from .forms import CustomerForm


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
def customer_list(request):
    shop = get_user_shop(request.user)

    customers = Customer.objects.filter(shop=shop).order_by('name')

    return render(request, 'sales/customer_list.html', {
        'customers': customers,
    })


@login_required
def customer_create(request):
    shop = get_user_shop(request.user)

    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.shop = shop
            customer.save()

            return redirect('customer_detail', pk=customer.pk)

    else:
        form = CustomerForm()

    return render(request, 'sales/customer_create.html', {
        'form': form,
    })


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