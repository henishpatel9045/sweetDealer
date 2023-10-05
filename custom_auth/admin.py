from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _

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
    list_display = ("username",)
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

    def get_queryset(self, request):
        return super().get_queryset(request).filter()
