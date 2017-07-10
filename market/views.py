from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from django.db.models import Sum
from datetime import datetime
from utils.common import format_body
from models import Banner, GoodsClassify, GroupBuy, GroupBuyGoods, GoodsGallery
from serializers import GoodsClassifySerializer, GroupBuySerializer,GroupBuyGoodsSerializer, BannerSerializer
from serializers import UploadImageSerializer
from ilinkgo.config import image_path
from iuser.models import AgentOrder, UserProfile

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


class AgentHomePageList(APIView):
    def get(self, request):
        agent_code = request.GET.get('agent_code')
        agent_user = UserProfile.objects.get(openid=agent_code)
        res = []
        classifies = GroupBuy.objects.filter(agentorder__user=agent_user.id, end_time__gt=datetime.now()).values('goods_classify').distinct()
        path = image_path()
        for classify in classifies:
            classify = GoodsClassify.objects.get(pk=classify['goods_classify'])
            classify_serializer = GoodsClassifySerializer(classify)
            group_buy = GroupBuy.objects.filter(agentorder__user=agent_user.id,
                                                end_time__gt=datetime.now(),goods_classify=classify.id).order_by('-add_time').first()
            agent_order = AgentOrder.objects.get(group_buy=group_buy.id, user=agent_user.id)
            group_buy_goods = GroupBuyGoods.objects.filter(id__in=str(agent_order.goods_ids).split(','))
            goods_info = []
            for goods in group_buy_goods:
                image = GoodsGallery.objects.filter(goods=goods.goods_id, is_primary=1).first()
                goods_info.append({
                    'goods_id': goods.id,
                    'image': path + image.image.url
                })
            res.append({
                'classify': classify_serializer.data,
                'goods': goods_info
            })

        return Response(format_body(1, 'Success', res))


class GroupBuyList(APIView):
    def get(self, request, format=None):
        """group_buy_list"""
        classify_id = request.GET.get('classify', '1')
        agent_code = request.GET.get('agent_code' ,'')

        classify = GoodsClassify.objects.filter(pk=classify_id).first()
        classify_serializer = GoodsClassifySerializer(classify)
        if agent_code:
            user = UserProfile.objects.get(openid=agent_code)
            group_buy = GroupBuy.objects.filter(goods_classify=classify_id, agentorder__user=user.id)
        else:
            group_buy = GroupBuy.objects.filter(goods_classify=classify_id)

        group_buy_serializer = GroupBuySerializer(group_buy, many=True)

        data = classify_serializer.data
        data['group_buy'] = group_buy_serializer.data

        return Response(format_body(1, 'success', data))


class GoodsList(APIView):
    def get(self, request):
        """group_buy_detail"""
        group_buy_id = request.GET.get('group_buy', '1')
        agent_code = request.GET.get('agent_code' ,'')

        group_buy = GroupBuy.objects.filter(pk=group_buy_id).first()
        group_buy_serializer = GroupBuySerializer(group_buy)

        class_serializer = GoodsClassifySerializer(group_buy.goods_classify)
        if agent_code:
            agent_user = UserProfile.objects.get(openid=agent_code)
            agent_order = AgentOrder.objects.get(group_buy=group_buy.id, user=agent_user.id)
            goods = GroupBuyGoods.objects.filter(id__in=str(agent_order.goods_ids).split(','))
        else:
            goods = GroupBuyGoods.objects.filter(group_buy=group_buy.id)

        goods_serializer = GroupBuyGoodsSerializer(goods, many=True)

        res = group_buy_serializer.data
        res['classify'] = class_serializer.data
        res['group_buy_goods'] = goods_serializer.data

        return Response(format_body(1, 'success', res))


class GroupBuyGoodsDetail(APIView):
    def get(self, request, format=None):
        """goods_detail """
        goods_id = request.GET.get('goods', '1')
        agent_code = request.GET.get('agent_code' ,'')

        try:
            goods = GroupBuyGoods.objects.get(pk=goods_id)
        except GroupBuyGoods.DoesNotExist:
            return Response(format_body(0,'Object does not exist',''))

        serializer = GroupBuyGoodsSerializer(goods)
        path = image_path()

        for image_itme in serializer.data['goods']['images']:
            image_itme['image'] = path + image_itme['image']

        res = serializer.data
        # if agent_code:
        #     generic_orders = GenericOrder.objects.filter(agent_code=agent_code, goods=goods_id)
        #     purchased = generic_orders.aggregate(Sum('quantity'))['quantity__sum']
        #     res['stock'] -=  purchased

        return Response(format_body(1, 'success', res))


class UploadImageVIew(APIView):
    def post(self, request):
        if request.data.has_key('imgFile'):
            image = request.data['imgFile']
            destination = open('images/' + image.name, 'wb+')
            for chunk in image.chunks():
                destination.write(chunk)
                destination.close()
            return Response({'error': 0, 'url':  image_path() + 'images/'+image.name})
        return Response({'error':1, 'message': 'file error'})