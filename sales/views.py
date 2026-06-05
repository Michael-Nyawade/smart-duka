from django.shortcuts import render, get_object_or_404
from .models import Sale, Customer


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
