# Generated by Django 4.1.7 on 2023-04-01 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_topsales_compare_at_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topsales',
            name='compare_at_price',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='Compare_at_price'),
        ),
        migrations.AlterField(
            model_name='topsales',
            name='price',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='Price'),
        ),
    ]
