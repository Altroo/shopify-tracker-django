from django.contrib import admin
from django.contrib.admin import ModelAdmin
from shops.models import Shops


class CustomShopsAdmin(ModelAdmin):
    list_display = ('pk', 'shop_url', 'availability', 'track_enabled')
    search_fields = ('shop_url', )
    list_editable = ('track_enabled',)
    ordering = ('-pk',)
    list_filter = ('availability', 'track_enabled',)
    date_hierarchy = 'created_date'


admin.site.register(Shops, CustomShopsAdmin)
