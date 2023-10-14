from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _

from core.models import Order

User = get_user_model()


class Dealer(User):
    class Meta:
        proxy = True
        verbose_name = "Dealer"
        verbose_name_plural = "Dealers"

    def save(self):
        if self.pk is None:
            self.password = "dealer@123"

        self.is_dealer = True
        self.is_staff = True
        return super().save()


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "total_orders",
        "total_amount",
        "amount_submitted",
        "current_amount",
    )
    search_fields = ("username",)
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username",)}),
        (
            _("Personal info"),
            {"fields": ("name",)},
        ),
        (_("Important dates"), {"fields": ("date_joined",)}),
    )

    def total_orders(self, obj):
        print(self.orders)
        return sum(x[0] == obj.pk for x in self.orders)

    def total_amount(self, obj):
        return str(sum(x[1] for x in self.orders if x[0] == obj.pk)) + " ₹"

    def amount_submitted(self, obj):
        return str(sum(x[1] for x in self.orders if x[0] == obj.pk and x[3])) + " ₹"

    def current_amount(self, obj):
        return (
            str(
                sum(x[1] for x in self.orders if x[0] == obj.pk and (x[2] and not x[3]))
            )
            + " ₹"
        )

    def changelist_view(self, request, extra_context=None):
        self.orders = (
            Order.objects.prefetch_related("bill_book", "bill_book__dealer")
            .all()
            .values_list(
                "bill_book__dealer__pk",
                "total_amount",
                "payment_received_to_dealer",
                "final_payment_received",
                "items",
            )
        )
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_dealer=True)


@admin.register(User)
class CustomUser(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("name",)},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
