# Generated by Django 4.2.6 on 2023-10-14 12:41

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_order_options_rename_book_order_bill_book_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='bill_image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True),
        ),
    ]
