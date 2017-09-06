
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Sum
from datetime import datetime
from utils.common import format_body, thumbnail
from models import Banner, GoodsClassify, GroupBuy, GroupBuyGoods, GoodsGallery
from serializers import GoodsClassifySerializer, GroupBuySerializer,GroupBuyGoodsSerializer, BannerSerializer
from ilinkgo.config import image_path
from iuser.models import AgentOrder, UserProfile, GenericOrder

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
        return Response(format_body(1, 'Success', {'images': banner_serializer.data}))


class HomePageList(APIView):
    def get(self, request, format=None):
        path = image_path()
        res = []
        goods_classify = GoodsClassify.objects.all()

        for classify in goods_classify:
            group_buy = GroupBuy.objects.filter(goods_classify=classify.id,end_time__gt=datetime.now(), on_sale=True).order_by('-add_time').first()

            if(group_buy):
                goods_info = []
                group_buy_goods = GroupBuyGoods.objects.filter(group_buy=group_buy.id)[:6]
                for goods in group_buy_goods:
                    gallery =  GoodsGallery.objects.filter(goods=goods.goods_id, is_primary=1).first()
                    goods_info.append({
                        'goods_id': goods.id,
                        'image': path + thumbnail(gallery.image.url) if gallery else ''
                    })
            else:
                continue

            classify_info = {
                'id': classify.id,
                'name': classify.name,
                'desc':  classify.desc,
                'image': path + classify.image.url,
                'icon': path + classify.icon.url
            }

            res.append({'classify': classify_info, 'goods': goods_info})

        return Response(format_body(1, 'Success', res))


class AgentHomePageList(APIView):
    def get(self, request):
        agent_code = request.GET.get('agent_code')
        try:
            agent_user = UserProfile.objects.get(openid=agent_code)
        except UserProfile.DoesNotExist:
            return Response(format_body(0, 'agent user does not exist', ''))

        res = []
        classifies = GroupBuy.objects.filter(agentorder__user=agent_user.id, end_time__gt=datetime.now(), on_sale=True).values('goods_classify').distinct()
        path = image_path()
        for classify in classifies:
            classify = GoodsClassify.objects.get(pk=classify['goods_classify'])
            classify_serializer = GoodsClassifySerializer(classify)
            group_buy = GroupBuy.objects.filter(agentorder__user=agent_user.id,
                                                end_time__gt=datetime.now(),
                                                on_sale=True,
                                                goods_classify=classify.id).order_by('-add_time').first()
            agent_order = AgentOrder.objects.get(group_buy=group_buy.id, user=agent_user.id)
            group_buy_goods = GroupBuyGoods.objects.filter(id__in=str(agent_order.goods_ids).split(','))
            goods_info = []
            for goods in group_buy_goods:
                image = GoodsGallery.objects.filter(goods=goods.goods_id, is_primary=1).first()
                goods_info.append({
                    'goods_id': goods.id,
                    'image': path + thumbnail(image.image.url) if image else ''
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
            group_buy = GroupBuy.objects.filter(goods_classify=classify_id,
                                                agentorder__user=user.id,
                                                on_sale=True,
                                                end_time__gt=datetime.now())
        else:
            group_buy = GroupBuy.objects.filter(goods_classify=classify_id,
                                                end_time__gt=datetime.now(),
                                                on_sale=True
                                                )

        group_buy_serializer = GroupBuySerializer(group_buy, many=True)

        data = classify_serializer.data
        data['group_buy'] = group_buy_serializer.data

        return Response(format_body(1, 'Success', data))


class GroupBuyDetailView(APIView):
    def get(self, request):
        """group_buy_detail"""
        group_buy_id = request.GET.get('group_buy', '1')
        agent_code = request.GET.get('agent_code' ,'')
        try:
            group_buy = GroupBuy.objects.filter(pk=group_buy_id).first()
        except GroupBuy.DoesNotExist:
            return Response(format_body(0, 'Object does not exist', ''))
        group_buy_serializer = GroupBuySerializer(group_buy)

        class_serializer = GoodsClassifySerializer(group_buy.goods_classify)
        if agent_code:
            agent_user = UserProfile.objects.get(openid=agent_code)
            agent_order = AgentOrder.objects.get(group_buy=group_buy.id, user=agent_user.id)
            goods = GroupBuyGoods.objects.filter(id__in=str(agent_order.goods_ids).split(','))
        else:
            goods = GroupBuyGoods.objects.filter(group_buy=group_buy.id)

        goods_serializer = GroupBuyGoodsSerializer(goods, many=True)

        # for goods in goods_serializer.data:
        #     goods['stock'] -=  GroupBuyGoodsDetail.purchased_amount(goods['id'])

        res = group_buy_serializer.data
        res['classify'] = class_serializer.data
        res['group_buy_goods'] = goods_serializer.data

        return Response(format_body(1, 'Success', res))


class GroupBuyGoodsDetail(APIView):
    def get(self, request, format=None):
        """goods_detail """
        goods_id = request.GET.get('goods', '1')
        # agent_code = request.GET.get('agent_code' ,'')

        try:
            goods = GroupBuyGoods.objects.get(pk=goods_id)
        except GroupBuyGoods.DoesNotExist:
            return Response(format_body(0,'Object does not exist',''))

        serializer = GroupBuyGoodsSerializer(goods)
        path = image_path()

        # for image_itme in serializer.data['goods']['images']:
        #     image_itme['image'] = path + image_itme['image']

        res = serializer.data

        # res['stock'] -= self.purchased_amount(goods_id)

        return Response(format_body(1, 'Success', res))

    @staticmethod
    def purchased_amount(goods_id):
        generic_orders = GenericOrder.objects.filter(goods=goods_id, status=1)
        purchased = generic_orders.aggregate(Sum('quantity'))['quantity__sum']
        return purchased or 0


class UploadImageView(APIView):
    def post(self, request):
        if request.data.has_key('imgFile'):
            import os, time
            from utils.common import random_str

            image = request.data['imgFile']

            goods_detail_path = "images/GoodsDetail/{}-{}/".format(time.strftime('%Y'), time.strftime('%m'))
            if not os.path.exists(goods_detail_path):
                os.makedirs(goods_detail_path)

            image_name = image.name.split('.')[0] + '_' + random_str() + '.' + image.name.split('.')[-1]
            destination = open(goods_detail_path + image_name, 'wb+')
            for chunk in image.chunks():
                destination.write(chunk)
                destination.close()
            return Response({
                'error': 0,
                'url':  image_path() + goods_detail_path +image_name,
                'width': '100%',
                'height': 'auto'
            })
        return Response({'error':1, 'message': 'file error'})


class FileManagerView(APIView):
    def get(self, request):
        import os
        from ilinkgo.settings import BASE_DIR
        req_path = request.GET.get('path')
        file_list = list()
        path = BASE_DIR + '/images/' + req_path

        for filename in os.listdir(path):
            item = dict()
            _file = path + filename
            if os.path.isdir(_file):
                item['has_file'] = True
                item['is_dir'] = True
                item['is_photo'] = False
            elif os.path.splitext(_file)[1] in ['.png', '.jpg', '.gif']:
                item['is_photo'] = True
                item['is_dir'] = False
            else:
                continue

            item['filename'] = filename
            item['filesize'] = os.path.getsize(_file)
            item['datetime'] = datetime.fromtimestamp(os.path.getmtime(_file)).strftime('%Y-%m-%d %H:%M:%S')

            file_list.append(item)

        temp_req_path = req_path.split('/')
        if len(temp_req_path) > 1:
            temp_req_path.pop(-2)
        moveup_dir_path = '/'.join(temp_req_path)

        data = {
            "moveup_dir_path": moveup_dir_path ,
            "current_dir_path": req_path,
            "total_count": 23,
            "current_url": image_path() +'images/' + req_path,
            'file_list': file_list
        }
        return Response(data)