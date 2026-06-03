from django.shortcuts import render, get_object_or_404
from .models import Sale


def sale_receipt_view(request, receipt_number):

    sale = get_object_or_404(Sale, receipt_number=receipt_number)

    context = {
        'sale': sale
    }

    return render(request, 'sales/receipt.html', context)