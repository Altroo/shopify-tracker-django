from django.db import models
from django.db.models import Model


class Shops(Model):
    shop_url = models.URLField(max_length=255, blank=False, null=False, default=None, unique=True)
    currency = models.CharField(max_length=50, blank=False, null=False, default=None)
    country = models.CharField(max_length=255, blank=False, null=False, default=None)
    availability = models.BooleanField(verbose_name='Available', default=True)
    track_enabled = models.BooleanField(verbose_name='Tracking', default=True)
    has_products = models.BooleanField(verbose_name='Has products', default=False)
    site_date = models.DateField(verbose_name='Site original date',
                                 default=None, blank=True, null=True)
    checked = models.BooleanField(verbose_name='Checked', default=False)
    created_date = models.DateTimeField(verbose_name='Created date', editable=False, auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(verbose_name='Updated date', editable=False, auto_now=True)

    def __str__(self):
        return '{}'.format(self.shop_url)

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'


class Configs(Model):
    interval = models.IntegerField(verbose_name='Interval', default=48)
    last_used_date = models.DateField(verbose_name='Last used date', default=None,
                                      blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.interval)

    class Meta:
        verbose_name = 'Config'
        verbose_name_plural = 'Configs'


class Proxies(Model):
    schema = models.CharField(verbose_name='Schema', max_length=5, blank=False, null=False, default=None)
    ip = models.CharField(max_length=255, blank=False, null=False, default=None, unique=True)

    def __str__(self):
        return '{}://{}'.format(self.schema, self.ip)

    class Meta:
        verbose_name = 'Proxy'
        verbose_name_plural = 'Proxies (2400)'
