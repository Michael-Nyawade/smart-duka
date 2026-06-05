from django.shortcuts import render, get_object_or_404, redirect
from .models import Sale, Customer, CreditPayment


def sale_receipt_view(request, receipt_number):

    sale = get_object_or_404(Sale, receipt_number=receipt_number)

    context = {
        'sale': sale
    }

    return render(request, 'sales/receipt.html', context)


def customer_detail(request, pk):

    customer = get_object_or_404(Customer, pk=pk)

    sales = customer.sales.all()
    payments = customer.credit_payments.all()

    context = {
        'customer': customer,
        'sales': sales,
        'payments': payments,
    }

    return render(request, 'sales/customer_detail.html', context)


def add_payment(request, pk):

    customer = get_object_or_404(Customer, pk=pk)

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
