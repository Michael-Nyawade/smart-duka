from django.contrib import admin
from .models import Sale, Customer, CreditPayment, SaleItem, CashierShift, AuditLog


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleItemInline]

    list_display = (
        'receipt_number',
        'customer',
        'payment_method',
        'created_at',
    )

    list_filter = (
        'payment_method',
        'created_at',
    )

    search_fields = (
        'items__product__name',
    )

    # Prevent editing or deleting sales
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    def view_customer(self, obj):
        from django.urls import reverse
        return f"/sales/customers/{obj.id}/"
    view_customer.short_description = "Profile"

    list_display = (
        'name',
        'phone_number',
        'outstanding_balance',
        'view_customer',
    )

    search_fields = (
        'name',
        'phone_number',
    )


@admin.register(CreditPayment)
class CreditPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'amount',
        'created_at',
    )

    search_fields = (
        'customer__name',
    )


@admin.register(CashierShift)
class CashierShiftAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'opened_at',
        'closed_at',
        'is_active',
    )

    search_fields = (
        'user__username',
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'action',
        'timestamp',
    )

    search_fields = (
        'user__username',
        'action',
    )
