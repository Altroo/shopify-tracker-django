# Generated by Django 4.1.3 on 2022-11-20 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shops',
            name='shop_url',
            field=models.URLField(default=None, max_length=255, unique=True),
        ),
    ]
