from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from shops.models import Shops
from products.models import Products
from products.serializers import ProductSerializer


class ProductsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        shop_url = request.data.get("shop_url")
        product = request.data.get("product")
        try:
            shop = Shops.objects.get(shop_url=shop_url)
            if isinstance(product, list):
                serializer = ProductSerializer(data={
                    'shop': shop,
                    'product': product,
                }, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                else:
                    raise ValidationError(serializer.errors)
            elif isinstance(product, str):
                serializer = ProductSerializer(data={
                    'shop': shop,
                    'product': product,
                })
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                else:
                    raise ValidationError(serializer.errors)
        except Shops.DoesNotExist:
            error = {'Error': 'Shop url not found.'}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request, *args, **kwargs):
        shop_url = request.data.get("shop_url")
        product = request.data.get("product")
        try:
            shop = Shops.objects.get(shop_url=shop_url)
            if isinstance(product, list):
                Products.objects.bulk_update(shop=shop, product=product)
            elif isinstance(product, str):
                Products.objects.update(shop=shop, product=product)
            return Response(data={'response': 'products updated.'}, status=status.HTTP_200_OK)
        except Shops.DoesNotExist:
            error = {'Error': 'Shop url not found.'}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)
