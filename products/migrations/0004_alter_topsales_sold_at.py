# Generated by Django 4.1.7 on 2023-04-01 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_topsales'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topsales',
            name='sold_at',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Sold at'),
        ),
    ]
