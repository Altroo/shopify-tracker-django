from django.contrib import admin
from django.contrib.admin import ModelAdmin
from shops.models import Shops, Configs, Proxies
from django.utils.html import format_html


class CustomShopsAdmin(ModelAdmin):
    list_display = ('pk', 'get_shop_url', 'has_products', 'currency', 'country', 'availability', 'track_enabled',
                    'checked', 'created_date', 'updated_date', 'site_date')
    search_fields = ('shop_url', 'currency', 'country', 'site_date')
    list_editable = ('has_products', 'track_enabled', 'availability', 'checked')
    ordering = ('-pk',)
    list_filter = ('has_products', 'checked', 'availability', 'track_enabled', 'currency', 'country', 'site_date', 'has_products')
    date_hierarchy = 'created_date'

    @admin.display(description='Shop url')
    def get_shop_url(self, obj):
        shop_url = obj.shop_url
        html = f"<a href='{shop_url}/products.json' target='_blank'>{shop_url}</a>"
        return format_html(html)


class CustomConfigsAdmin(ModelAdmin):
    list_display = ('pk', 'interval', 'last_used_date',)

    # # Add permission removed
    # def has_add_permission(self, *args, **kwargs):
    #     return False
    #
    # # Delete permission removed
    # def has_delete_permission(self, *args, **kwargs):
    #     return False


class CustomProxiesAdmin(ModelAdmin):
    list_display = ('pk', 'schema', 'ip',)
    search_fields = ('schema', 'ip',)
    ordering = ('-pk',)


admin.site.register(Shops, CustomShopsAdmin)
admin.site.register(Configs, CustomConfigsAdmin)
admin.site.register(Proxies, CustomProxiesAdmin)
