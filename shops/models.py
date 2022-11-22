from django.db import models
from django.db.models import Model


class Shops(Model):
    shop_url = models.URLField(max_length=255, blank=False, null=False, default=None, unique=True)
    availability = models.BooleanField(verbose_name='Available', default=True)
    track_enabled = models.BooleanField(verbose_name='Tracking', default=True)
    created_date = models.DateTimeField(verbose_name='Created date', editable=False, auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(verbose_name='Updated date', editable=False, auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.shop_url, self.availability)

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
