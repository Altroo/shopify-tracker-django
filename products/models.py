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
