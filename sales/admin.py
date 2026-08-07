from django.contrib import admin
from .models import Sale, Customer, CreditPayment, SaleItem, CashierShift, AuditLog
from core.utils import get_user_shop


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

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            shop=get_user_shop(request.user)
        )


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

    # Enforce shop assignment on save
    def save_model(self, request, obj, form, change):
        if not obj.shop:
            obj.shop = get_user_shop(request.user)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            shop=get_user_shop(request.user)
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
