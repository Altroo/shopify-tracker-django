# Generated by Django 4.1.7 on 2023-03-09 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0012_remove_shops_picked'),
    ]

    operations = [
        migrations.AddField(
            model_name='shops',
            name='has_products',
            field=models.BooleanField(default=False, verbose_name='Has products'),
        ),
    ]
