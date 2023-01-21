from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from shops.models import Shops, Configs
from shops.serializers import ShopSerializer


class ShopView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        shop_urls = request.data.get("shop_urls")
        if isinstance(shop_urls, list):
            serializer = ShopSerializer(data=shop_urls, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                raise ValidationError(serializer.errors)
        elif isinstance(shop_urls, str):
            serializer = ShopSerializer(data=shop_urls)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                raise ValidationError(serializer.errors)

    @staticmethod
    def delete(request, *args, **kwargs):
        shop_urls = request.data.get("shop_urls")
        if isinstance(shop_urls, list):
            for shop_url in shop_urls:
                try:
                    shop = Shops.objects.get(shop_url=shop_url)
                    shop.delete()
                except Shops.DoesNotExist:
                    pass
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif isinstance(shop_urls, str):
            try:
                shop = Shops.objects.get(shop_url=shop_urls)
                shop.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Shops.DoesNotExist:
                pass


class ConfigsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def patch(request, *args, **kwargs):
        interval = request.data.get("interval")
        config = Configs.objects.all()
        if len(config) == 0:
            Configs.objects.create(interval=interval)
        else:
            config.update(interval=interval)
        return Response(data={'response': 'configs added/updated.'}, status=status.HTTP_200_OK)
