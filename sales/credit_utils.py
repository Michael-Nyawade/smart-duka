from .models import Customer


def get_customers_with_balances():
    return [
        customer
        for customer in Customer.objects.all()
        if customer.outstanding_balance() > 0
    ]


def get_total_outstanding_credit():
    return sum(
        customer.outstanding_balance()
        for customer in Customer.objects.all()
    )


def get_top_debtors(limit=5):

    customers = sorted(
        get_customers_with_balances(),
        key=lambda customer: customer.outstanding_balance(),
        reverse=True
    )

    return customers[:limit]