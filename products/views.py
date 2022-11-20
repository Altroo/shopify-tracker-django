from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
# from shops.models import


class BlankView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        result = []
        return Response(data=result, status=status.HTTP_200_OK)