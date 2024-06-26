# Generated by Django 4.1.7 on 2023-04-01 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0014_proxies'),
        ('products', '0002_products_created_date_products_updated_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopSales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_title', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Product title')),
                ('product_url', models.URLField(blank=True, default=None, max_length=255, null=True, verbose_name='Product url')),
                ('variant', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Variant')),
                ('thumbnail', models.URLField(blank=True, default=None, max_length=255, null=True, verbose_name='Product thumbnail')),
                ('sku', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='SKU')),
                ('quantity_sold', models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Quantity sold')),
                ('price', models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Price')),
                ('sold_at', models.DateTimeField(blank=True, default=None, editable=False, null=True, verbose_name='Sold at')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_top_sales', to='shops.shops', verbose_name='Shop url')),
            ],
            options={
                'verbose_name': 'Top Sale',
                'verbose_name_plural': 'Top Sales',
            },
        ),
    ]
