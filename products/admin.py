from django.contrib import admin
from django.contrib.admin import ModelAdmin
from products.models import Products


class CustomProductsAdmin(ModelAdmin):
    list_display = ('pk', 'shop', 'show_product', 'created_date', 'updated_date')
    search_fields = ('pk', 'shop__shop_url')
    ordering = ('-pk',)
    date_hierarchy = 'created_date'

    @staticmethod
    def show_product(obj):
        return str(obj.product)[0:30] + '...'


admin.site.register(Products, CustomProductsAdmin)

