# Generated by Django 4.1.3 on 2022-11-21 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0003_alter_shops_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='shops',
            name='track_enabled',
            field=models.BooleanField(default=True, verbose_name='Tracking'),
        ),
    ]
