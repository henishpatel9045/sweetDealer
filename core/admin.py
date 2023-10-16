from typing import Any
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.db import transaction

from core.models import Item, Order

User = get_user_model()

admin.site.site_header = "Vadiparti Yuvak Mandal"
# @admin.register(BillBook)
# class BillBookAdmin(admin.ModelAdmin):
#     autocomplete_fields = ("dealer",)
#     search_fields = ("dealer__username",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order_quantity",
        "quantity_boxed",
    )

    def quantity_boxed(self, obj):
        total = 0
        for pack in obj.packs:
            total += (pack["quantity_ready"] or 0) * (
                int(pack["box"].split()[0]) / (1 if "KG" in pack["box"] else 1000)
            )
        return str(total) + " KG"

    def order_quantity(self, obj):
        total_quantity = sum(
            sum(
                (int(p["box"].split()[0]) / (1 if "KG" in p["box"] else 1000))
                * p["quantity"]
                for p in bill.items
                if p["item"] == obj.name
            )
            for bill in self.bills
        )
        return str(total_quantity) + " KG"

    def changelist_view(self, request, extra_context=None):
        self.bills = Order.objects.all()
        return super().changelist_view(request, extra_context)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "dealer",
        "customer",
        "total_amount",
        "status",
        "payment_received_to_dealer",
        "final_payment_received",
        "created_at",
    )
    search_fields = (
        "order_number",
        "phone",
        "customer",
        "dealer__username",
    )
    list_filter = (
        "status",
        "payment_received_to_dealer",
        "final_payment_received",
    )
    autocomplete_fields = ("dealer",)
    actions = ("calculate_total_amount",)

    def calculate_total_amount(self, request, queryset):
        with transaction.atomic():
            for q in queryset:
                q.save()

    def save_model(self, request, obj, form, change):
        try:
            return super().save_model(request, obj, form, change)
        except Exception as e:
            msg = e.args[0]
            msg = format_html(f'{msg} <a href="{request.path}">Open Form</a>')
            return messages.error(request, msg)
