# Generated by Django 5.2.1 on 2025-07-11 11:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_product_is_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='backup_riders',
            field=models.ManyToManyField(blank=True, limit_choices_to={'role': 'rider'}, related_name='backup_orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_rider',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'rider'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('shipped', 'Shipped'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered')], default='pending', max_length=20),
        ),
    ]
