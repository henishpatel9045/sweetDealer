# Generated by Django 4.2.6 on 2024-02-16 10:51

import cloudinary.models
import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import django_jsonform.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0, 'Amount must be positive.')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True, null=True)),
                ('packs', django_jsonform.models.fields.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order_number', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('customer', models.CharField(max_length=200)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('city_area', models.CharField(blank=True, max_length=300, null=True)),
                ('address', models.TextField(blank=True, default='')),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12)),
                ('items', django_jsonform.models.fields.JSONField()),
                ('bill_image', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('ready', 'ready'), ('delivered', 'delivered'), ('cancelled', 'cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('order_picked_at', models.DateTimeField(blank=True, null=True)),
                ('order_picked_by', models.CharField(blank=True, choices=[('Dealer', 'Dealer'), ('Customer', 'Customer'), ('City Outlet', 'City Outlet')], max_length=150, null=True)),
                ('payment_received_to_dealer', models.BooleanField(default=False)),
                ('final_payment_received', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
