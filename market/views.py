from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status

from models import Banner
from serializers import BannerSerializer
# Create your views here.

# @api_view(['GET'])
# def api_root(request, format=None):
#     return Response({
#         'banner': reverse('banner', request=request, format=format),
#     })


class BannerList(generics.ListAPIView):
    queryset = Banner.objects.filter(is_show=1)
    serializer_class = BannerSerializer