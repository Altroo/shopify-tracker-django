from django.db import models
from django.db.models import Model
from shops.models import Shops


class Products(Model):
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE,
                             verbose_name='Shop url', related_name='shop_product')
    product = models.JSONField(blank=False, null=False)
    created_date = models.DateTimeField(verbose_name='Created date', editable=False, auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(verbose_name='Updated date', editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.shop.shop_url)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class TopSales(Model):
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name='Shop url', related_name='shop_top_sales')
    product_title = models.CharField(verbose_name='Product title', max_length=255, blank=True, null=True, default=None)
    product_url = models.URLField(verbose_name='Product url', max_length=255, blank=True, null=True, default=None)
    variant = models.CharField(verbose_name='Variant', max_length=255, blank=True, null=True, default=None)
    thumbnail = models.URLField(verbose_name='Product thumbnail', max_length=255, blank=True, null=True,
                                default=None)
    sku = models.CharField(verbose_name='SKU', max_length=255, blank=True, null=True, default=None)
    quantity_sold = models.PositiveIntegerField(verbose_name='Quantity sold', default=None, null=True, blank=True)
    price = models.FloatField(verbose_name='Price', default=None, null=True, blank=True)
    compare_at_price = models.FloatField(verbose_name='Compare_at_price', default=None, null=True, blank=True)
    sold_at = models.DateTimeField(verbose_name='Sold at', blank=True, null=True, default=None)

    def __str__(self):
        return '{}'.format(self.shop.shop_url)

    class Meta:
        # unique_together = (('product_url', 'sku'),)
        verbose_name = 'Top Sale'
        verbose_name_plural = 'Top Sales'
