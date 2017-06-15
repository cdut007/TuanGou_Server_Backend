from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


from models import Banner, GoodsClassify, GroupBuy, GroupBuyGoods, GoodsGallery
from serializers import GoodsClassifySerializer, GroupBuySerializer,GroupBuyGoodsSerializer, BannerSerializer
from ilinkgo.dbConfig import image_path

# Create your views here.

# @api_view(['GET'])
# def api_root(request, format=None):
#     return Response({
#         'banner': reverse('banner', request=request, format=format),
#         'home_page_list': reverse('home_page_list', request=request, format=format),
#         'group_buy_list': reverse('group_buy_list', request=request, format=format),
#         'group_buy_detail': reverse('group_buy_detail', request=request, format=format),
#         'goods_detail': reverse('goods_detail', request=request, format=format)
#     })


class BannerList(APIView):
    def get(self,request, format=None):
        banners = Banner.objects.filter(is_show=1)
        banner_serializer =  BannerSerializer(banners, many=True)
        return Response(format_body(1, 'success', {'images': banner_serializer.data}))


class HomePageList(APIView):
    def get(self, request, format=None):
        path = image_path()
        res = []
        goods_classify = GoodsClassify.objects.all()

        for classify in goods_classify:
            group_buy = GroupBuy.objects.filter(goods_classify=classify.id).order_by('-add_time').first()

            if(group_buy):
                goods_info = []
                group_buy_goods = GroupBuyGoods.objects.filter(group_buy=group_buy.id)[:6]
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


class GroupBuyList(APIView):
    def post(self, request, pk, format=None):
        """
        group_buy_list/<classify_id>
        """
        classify = GoodsClassify.objects.filter(pk=pk).first()
        classify_serializer = GoodsClassifySerializer(classify)

        group_buy = GroupBuy.objects.filter(goods_classify=pk)
        group_buy_serializer = GroupBuySerializer(group_buy, many=True)

        data = classify_serializer.data
        data['group_buy'] = group_buy_serializer.data

        return Response(format_body(1, 'success', data))


class GoodsList(APIView):
    def get(self, request, pk):
        """
        group_buy_detail/<group_buy_id>
        """
        group_buy = GroupBuy.objects.filter(pk=pk).first()
        group_buy_serializer = GroupBuySerializer(group_buy)

        classify = GoodsClassify.objects.filter(id=group_buy.goods_classify_id).first()
        class_serializer = GoodsClassifySerializer(classify)

        goods = GroupBuyGoods.objects.filter(group_buy=group_buy.id)
        goods_serializer = GroupBuyGoodsSerializer(goods, many=True)

        res = group_buy_serializer.data
        res['classify'] = class_serializer.data
        res['group_buy_goods'] = goods_serializer.data

        return Response(format_body(1, 'success', res))


class GroupBuyGoodsDetail(APIView):
    def get(self, request, pk, format=None):
        """
        goods_detail/<goods_lid>
        """
        try:
            goods = GroupBuyGoods.objects.get(pk=pk)
        except GroupBuyGoods.DoesNotExist:
            return Response(format_body(0,'Object does not exist',''))

        serializer = GroupBuyGoodsSerializer(goods)
        path = image_path()

        for image_itme in serializer.data['goods']['images']:
            image_itme['image'] = path + image_itme['image']

        return Response(format_body(1, 'success', serializer.data))


def format_body(code, message, data):
    res = {
        'code': code,
        'message': message,
        'data': data
    }
    return res
