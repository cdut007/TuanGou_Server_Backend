from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status


from models import Banner, GoodsClassify, GroupBuy, GroupBuyGoods, GoodsGallery
from serializers import GoodsClassifySerializer, GroupBuySerializer,GroupBuyGoodsSerializer
from ilinkgo.dbConfig import image_path

# Create your views here.

# @api_view(['GET'])
# def api_root(request, format=None):
#     return Response({
#         'banner': reverse('banner', request=request, format=format),
#     })


class BannerList(APIView):
    def get(self,request, format=None):
        res = []
        path = image_path()
        banners = Banner.objects.filter(is_show=1)
        for image in banners:
            res.append(path + image.image.url)
        return Response(format_body(1, 'success', {'images': res}))


class GoodsClassifyList(generics.ListAPIView):
    queryset = GoodsClassify.objects.all()
    serializer_class = GoodsClassifySerializer


class GroupBuyList(APIView):
    def get(self, request, format=None):
        group_buy = GroupBuy.objects.all()
        serializer = GroupBuySerializer(group_buy, many=True)
        return Response(serializer.data)


class HomePageList(APIView):
    def get(self, request, format=None):
        path = image_path()
        res = []
        goods_classify = GoodsClassify.objects.all()

        for classify in goods_classify:
            group_buy = GroupBuy.objects.filter(goods_classify=classify.id).order_by('-add_time').first()

            if(group_buy):
                goods_info = []
                group_buy_goods = GroupBuyGoods.objects.filter(group_buy=group_buy.id)
                for goods in group_buy_goods:
                    image =  GoodsGallery.objects.filter(goods=goods.goods_id, is_primary=1).first()
                    goods_info.append({
                        'goods_id': goods.id,
                        'image': path + image.image.url
                    })
            else:
                continue

            classify_info = {
                'id': classify.id,
                'name': classify.name,
                'desc': classify.desc,
                'icon': image_path() + classify.icon.url
            }

            res.append({'classify': classify_info, 'goods': goods_info})

        return Response(format_body(1, 'success', res))


class GroupBuyGoodsDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            goods = GroupBuyGoods.objects.get(pk=pk)
        except GroupBuyGoods.DoesNotExist:
            return Response(format_body(0,'Object does not exist',''))

        serializer = GroupBuyGoodsSerializer(goods)
        path = image_path()

        for image_itme in serializer.data['goods']['images']:
            image_itme['image'] = path + image_itme['image']

        return Response(serializer.data)


class GroupBuyGoodsList(generics.RetrieveAPIView):
    queryset = GroupBuy.objects.all()
    serializer_class = GroupBuySerializer


def format_body(code, message, data):
    res = {
        'code': code,
        'message': message,
        'data': data
    }
    return res
