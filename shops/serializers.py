from rest_framework import serializers
from shops.models import Shops


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shops
        fields = ['shop_url']
