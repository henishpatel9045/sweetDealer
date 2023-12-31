# Generated by Django 4.2.6 on 2023-10-04 17:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="dealer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="items",
            field=models.ManyToManyField(through="core.OrderItem", to="core.item"),
        ),
        migrations.AddField(
            model_name="billbook",
            name="dealer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="billbook",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
