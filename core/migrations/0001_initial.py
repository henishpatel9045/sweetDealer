# Generated by Django 4.2.6 on 2023-10-04 17:07

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_jsonform.models.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BillBook",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("max_bills", models.IntegerField(default=0)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ExpenseTracker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=15,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Amount must be positive."
                            )
                        ],
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=500)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "packs",
                    django_jsonform.models.fields.JSONField(blank=True, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.CharField(max_length=200)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("city_area", models.CharField(blank=True, max_length=300, null=True)),
                ("address", models.TextField(blank=True, default="")),
                (
                    "amount_paid",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=12
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=12
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("ready", "Ready"),
                            ("delivered", "Delivered"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("order_picked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "order_picked_by",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Dealer", "Dealer"),
                            ("Customer", "Customer"),
                            ("City Outlet", "City Outlet"),
                        ],
                        max_length=150,
                        null=True,
                    ),
                ),
                ("payment_received_to_dealer", models.BooleanField(default=False)),
                ("final_payment_received", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "box",
                    models.CharField(
                        choices=[
                            ("250 G", "250 G"),
                            ("500 G", "500 G"),
                            ("1 KG", "1 KG"),
                            ("2 KG", "2 KG"),
                        ],
                        max_length=20,
                    ),
                ),
                ("quantity", models.IntegerField(default=0)),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.item"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.order"
                    ),
                ),
            ],
        ),
    ]
