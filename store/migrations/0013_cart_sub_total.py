# Generated by Django 4.2 on 2023-10-29 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_cart_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='sub_total',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
        ),
    ]
