# Generated by Django 5.2.1 on 2025-06-07 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_order_orderitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='is_ordered',
        ),
    ]
