from django.contrib import admin
from django.contrib.admin import ModelAdmin
from shops.models import Shops, Configs


class CustomShopsAdmin(ModelAdmin):
    list_display = ('pk', 'shop_url', 'availability', 'track_enabled', 'created_date', 'updated_date')
    search_fields = ('shop_url', )
    list_editable = ('track_enabled',)
    ordering = ('-pk',)
    list_filter = ('availability', 'track_enabled',)
    date_hierarchy = 'created_date'


class CustomConfigsAdmin(ModelAdmin):
    list_display = ('interval',)

    # # Add permission removed
    # def has_add_permission(self, *args, **kwargs):
    #     return False
    #
    # # Delete permission removed
    # def has_delete_permission(self, *args, **kwargs):
    #     return False


admin.site.register(Shops, CustomShopsAdmin)
admin.site.register(Configs, CustomConfigsAdmin)
