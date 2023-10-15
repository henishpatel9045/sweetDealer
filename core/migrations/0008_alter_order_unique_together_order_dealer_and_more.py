# Generated by Django 4.2.6 on 2023-10-15 16:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0007_order_bill_image'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='order',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='order',
            name='dealer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='order',
            unique_together={('dealer', 'order_number')},
        ),
        migrations.RemoveField(
            model_name='order',
            name='bill_book',
        ),
        migrations.DeleteModel(
            name='BillBook',
        ),
    ]