from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django_jsonform.models.fields import JSONField

from core.constants import OrderConstant, BoxConstant

model_box_choices = [
    (BoxConstant.BOX_250.value, BoxConstant.BOX_250.value),
    (BoxConstant.BOX_500.value, BoxConstant.BOX_500.value),
    (BoxConstant.BOX_1000.value, BoxConstant.BOX_1000.value),
    (BoxConstant.BOX_2000.value, BoxConstant.BOX_2000.value),
]

User = get_user_model()


class TimeUpdateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BillBook(TimeUpdateModel, models.Model):
    dealer = models.ForeignKey(User, related_name="billbook", on_delete=models.CASCADE)
    max_bills = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.pk)


class Item(models.Model):
    ITEMS_SCHEMA = {
        "type": "array",
        "title": "OrderItems",
        "items": {
            "type": "object",
            "keys": {
                "box": {
                    "type": "string",
                    "choices": [
                        BoxConstant.BOX_250.value,
                        BoxConstant.BOX_500.value,
                        BoxConstant.BOX_1000.value,
                        BoxConstant.BOX_2000.value,
                    ],
                },
                "price": {"type": "integer", "minimun": "0", "required": True},
                "quantity_ready": {"type": "integer", "minimun": "0", "default": 0},
            },
        },
        "minItems": 1,
    }

    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    packs = JSONField(schema=ITEMS_SCHEMA, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def save(self):
        for pack in self.packs:
            if pack["price"] < 0:
                raise Exception("Price must be positive.")
            if pack["quantity_ready"] is None:
                pack["quantity_ready"] = 0
            elif pack["quantity_ready"] < 0:
                raise Exception("Quantity must be positive.")
        super().save()


class OrderManage(models.Manager):
    def get_active(self):
        return self.exclude(status=OrderConstant.STATUS_CANCELLED.value)


def order_schema():
    return {
        "type": "array",
        "title": "OrderItems",
        "items": {
            "type": "object",
            "keys": {
                "item": {
                    "type": "string",
                    "choices": [i["name"] for i in Item.objects.all().values("name")],
                    "required": True,
                },
                "box": {
                    "type": "string",
                    "choices": [
                        BoxConstant.BOX_250.value,
                        BoxConstant.BOX_500.value,
                        BoxConstant.BOX_1000.value,
                        BoxConstant.BOX_2000.value,
                    ],
                    "required": True,
                },
                "quantity": {
                    "type": "number",
                    "minimun": "1",
                    "required": True,
                },
            },
        },
        "minItems": 1,
    }


class Order(TimeUpdateModel, models.Model):
    STATUS_CHOICES = (
        (OrderConstant.STATUS_PENDING.value, OrderConstant.STATUS_PENDING.value),
        (OrderConstant.STATUS_READY.value, OrderConstant.STATUS_READY.value),
        (OrderConstant.STATUS_DELIVERED.value, OrderConstant.STATUS_DELIVERED.value),
        (OrderConstant.STATUS_CANCELLED.value, OrderConstant.STATUS_CANCELLED.value),
    )

    PICKUP_OPTIONS = [
        ("Dealer", "Dealer"),
        ("Customer", "Customer"),
        ("City Outlet", "City Outlet"),
    ]

    book = models.ForeignKey(BillBook, related_name="orders", on_delete=models.CASCADE)
    customer = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, null=True, blank=True)
    city_area = models.CharField(max_length=300, null=True, blank=True)
    address = models.TextField(default="", blank=True)
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, blank=True
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, blank=True
    )
    items = JSONField(schema=order_schema)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=OrderConstant.STATUS_PENDING.value,
    )

    order_picked_at = models.DateTimeField(null=True, blank=True)
    order_picked_by = models.CharField(
        max_length=150, choices=PICKUP_OPTIONS, null=True, blank=True
    )
    payment_received_to_dealer = models.BooleanField(default=False)
    final_payment_received = models.BooleanField(default=False)

    objects = OrderManage()

    def __str__(self) -> str:
        return str(self.pk)

    class Meta:
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        self.total_amount = self.get_total_amount()
        if self.amount_paid > self.total_amount:
            raise Exception("Amount paid cannot be greater than total amount.")
        if self.amount_paid == self.total_amount:
            self.final_payment_received = True
        else:
            self.final_payment_received = False
        super().save(*args, **kwargs)

    def get_total_amount(self):
        total = 0
        qs_items = Item.objects.all()
        for item in self.items:
            if item["quantity"] is None or item["quantity"] <= 0:
                raise Exception("Quantity must be positive.")
            item_obj = qs_items.get(name=item["item"])
            for pack in item_obj.packs:
                if pack["box"] == item["box"]:
                    total += pack["price"] * item["quantity"]
                    break
        return total


class ExpenseTracker(TimeUpdateModel, models.Model):
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0, "Amount must be positive.")],
    )
