# Generated by Django 4.1.7 on 2023-03-03 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0011_shops_picked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shops',
            name='picked',
        ),
    ]
