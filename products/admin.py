from django.contrib import admin
from django.contrib.admin import ModelAdmin
from products.models import Products, TopSales
from django.utils.html import format_html

class CustomProductsAdmin(ModelAdmin):
    list_display = ('pk', 'shop', 'show_product', 'created_date', 'updated_date')
    search_fields = ('pk', 'shop__shop_url')
    ordering = ('-pk',)
    list_filter = ('created_date', 'updated_date')
    date_hierarchy = 'created_date'

    @staticmethod
    def show_product(obj):
        return str(obj.product)[0:30] + '...'


class CustomTopSalesAdmin(ModelAdmin):
    list_display = ('pk', 'get_shop_url', 'get_product_name', 'get_product_url', 'get_variant', 'get_product_thumbnail',
                    'sku', 'quantity_sold', 'get_price', 'get_compare_at_price', 'sold_at')
    search_fields = ('pk', 'shop__shop_url', 'product_title')
    ordering = ('-pk',)
    list_filter = ('sold_at', 'quantity_sold', 'price', 'compare_at_price')
    date_hierarchy = 'sold_at'

    @admin.display(description='Shop url')
    def get_shop_url(self, obj):
        shop_url = obj.shop.shop_url
        html = f"<a href='{shop_url}' target='_blank'>{shop_url}</a>"
        return format_html(html)

    @admin.display(description='Product url')
    def get_product_url(self, obj):
        product_url = obj.product_url
        html = f"<a href='{product_url}' target='_blank'>{product_url[0:10] + '...'}</a>"
        return format_html(html)

    @admin.display(description='Thumbnail')
    def get_product_thumbnail(self, obj):
        thumbnail = obj.thumbnail
        html = f"<a href='{thumbnail}' target='_blank'>{thumbnail[0:10] + '...'}</a>"
        return format_html(html)

    @admin.display(description='Product name')
    def get_product_name(self, obj):
        return str(obj.product_title)[0:10] + '...'

    @admin.display(description='Variant')
    def get_variant(self, obj):
        return str(obj.variant)[0:10] + '...'

    @admin.display(description='Sold at price')
    def get_price(self, obj):
        currency = obj.shop.currency
        return f'{obj.price} {currency}'

    @admin.display(description='Previous price')
    def get_compare_at_price(self, obj):
        currency = obj.shop.currency
        return f'{obj.compare_at_price} {currency}'


admin.site.register(Products, CustomProductsAdmin)
admin.site.register(TopSales, CustomTopSalesAdmin)

