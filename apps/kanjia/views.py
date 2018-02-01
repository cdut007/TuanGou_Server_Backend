# _*_ coding:utf-8 _*_
import uuid
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from ilinkgo.settings import conf
from utils.common import format_body, raise_general_exception, dict_fetch_all
from utils.winxin import WeiXinAPI, WeiXinXml

from models import ActivityJoin, KanJiaLog, KanJiaActivity, KanJiaOrder, ActivityLatestTrack
from iuser.Authentication import Authentication
from iuser.models import UserProfile

    
class WxPayView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        quantity = int(request.data['quantity'])
        activity_id = request.data['activity_id']

        activity = KanJiaActivity.objects.get(activity_id=activity_id)
        if activity.quantity < quantity:
            return Response(format_body(25, 'Fail', u'当前剩余数量：'+str(activity.quantity)+'!'))

        order_rec = KanJiaOrder.objects.filter(
            owner = self.post.user_id,
            activity_id = activity_id,
            wx_result_code = 'SUCCESS'
        ).first()
        if order_rec:
            return Response(format_body(25, 'Fail', u'您已购买过当前商品了哦！'))

        wei_xin_api = WeiXinAPI()

        pay_money = int(activity.exchange_price * 100 * quantity)
        trade_no = KanJiaOrder.gen_trade_no()
        notify_url = conf.server_run_addr+'/v2/api.kanjia.pay.callback'
        user = UserProfile.objects.get(pk=self.post.user_id)

        wx_prepay_order = wei_xin_api.pay(activity.title,trade_no, pay_money, notify_url, user.openid_web)
        prepay_id = wx_prepay_order['prepay_id']

        KanJiaOrder.prepay(self.post.user_id, activity.activity_id, quantity, activity.exchange_price, pay_money, trade_no, prepay_id)

        params = wei_xin_api.pay_params(prepay_id)
        return Response(format_body(1, 'Success', params))


class WxPayCallBack(APIView):
    @raise_general_exception
    def post(self, request):
        from django.http import HttpResponse
        wx_callback_data = WeiXinXml.xml2json(request.body)
        KanJiaOrder.update_pay(wx_callback_data)
        res = WeiXinXml.json2xml({'return_code': 'SUCCESS','return_msg': ''})
        return HttpResponse(res,content_type="text/xml")


class KanJiaJoin(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        activity_id = request.data['activity_id']
        owner = self.post.user_id
        ActivityJoin.join(owner, activity_id)
        return Response(format_body(1, 'Success', ''))


class KanJiaKj(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self,request):
        owner = UserProfile.objects.get(sharing_code=request.data['sharing_code'])

        # 活动是否过期
        is_expire = KanJiaLog.is_expire(activity_id=request.data['activity_id'])
        if is_expire:
            return Response(format_body(24, 'Fail', u'当前活动已经过期了哦^V^！'))

        # 不能帮自己砍价
        if owner.id == self.post.user_id:
            return Response(format_body(21, 'Fail', u'您不能帮自己砍价哦！'))

        # 已经帮这位好友砍过
        kan_guo = KanJiaLog.is_kan_guo(owner.id, self.post.user_id, request.data['activity_id'])
        if kan_guo:
            return Response(format_body(20, 'Fail', u'您已经帮这位好友砍过价了哦！'))

        # 今天砍价的次数是否大于3次
        times_today = KanJiaLog.times_today(self.post.user_id)
        if times_today >= 3:
            return Response(format_body(23, 'Fail', u'您今天已经帮好友拆过3次红包了哦！'))

        money = KanJiaLog.kan_jia(owner.id, self.post.user_id, request.data['activity_id'])

        return Response(format_body(1, 'Success', {'money': money}))


class KanJiaIntro(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_activity_detail, sql_activity_ranking
        cursor = connection.cursor()

        sql_activity_detail = sql_activity_detail.format(activity_id = request.GET['activity_id'],_image_prefix=conf.image_url_prefix)
        cursor.execute(sql_activity_detail)
        activity_intro = dict_fetch_all(cursor)[0]

        sql_activity_ranking = sql_activity_ranking.format(activity_id=request.GET['activity_id'])
        cursor.execute(sql_activity_ranking)
        activity_ranking = dict_fetch_all(cursor)

        current_user = UserProfile.objects.get(pk=self.get.user_id)
        join_rec = ActivityJoin.objects.filter(owner=self.get.user_id, activity_id=request.GET['activity_id']).first()
        is_join = 1 if join_rec else 0
        wei_xin_api = WeiXinAPI()
        wx_info = wei_xin_api.user_info(current_user.openid_web)

        return Response(format_body(1, 'Success', {
            'intro': activity_intro,
            'ranking': activity_ranking,
            'current_user': {
                'is_subscribe': wx_info['subscribe'] if wx_info.has_key('subscribe') else 0,
                'sharing_code': current_user.sharing_code,
                'is_join': is_join
            },
            'country': u'新加坡'
        }))


class KanJiaDetail(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_activity_detail, sql_activity_user_info, sql_activity_kan_jia_logs
        owner = UserProfile.objects.get(sharing_code=request.GET['sharing_code'])

        cursor = connection.cursor()

        sql_activity_detail = sql_activity_detail.format(activity_id = request.GET['activity_id'],_image_prefix=conf.image_url_prefix)
        cursor.execute(sql_activity_detail)
        activity_intro = dict_fetch_all(cursor)[0]

        sql_activity_user_info = sql_activity_user_info.format(activity_id=request.GET['activity_id'],owner=owner.id)
        cursor.execute(sql_activity_user_info)
        owner_info = dict_fetch_all(cursor)[0]

        sql_activity_kan_jia_logs = sql_activity_kan_jia_logs.format(activity_id = request.GET['activity_id'],owner=owner.id)
        cursor.execute(sql_activity_kan_jia_logs)
        activity_kan_jia_logs = dict_fetch_all(cursor)

        owner_info['is_purchased'] = 1  if owner_info['wx_result_code']=='SUCCESS' else 0
        owner_info.pop('wx_result_code')

        current_user = UserProfile.objects.get(pk=self.get.user_id)
        if not current_user.sharing_code:
            current_user.sharing_code = uuid.uuid1()
            current_user.save()

        join_rec = ActivityJoin.objects.filter(owner=self.get.user_id, activity_id=request.GET['activity_id']).first()
        kanjia_rec = KanJiaLog.objects.filter(owner=owner.id, kj_user=self.get.user_id, activity_id=request.GET['activity_id']).first()
        is_kj = 1 if kanjia_rec else 0
        kj_money = kanjia_rec.money if kanjia_rec else 0
        is_join = 1 if join_rec else 0
        wei_xin_api = WeiXinAPI()
        wx_info = wei_xin_api.user_info(current_user.openid_web)
        is_subscribe = wx_info['subscribe'] if wx_info.has_key('subscribe') else 0

        ActivityLatestTrack.save_track(
            sharing_code = request.GET['sharing_code'],
            activity_id = request.GET['activity_id'],
            user_id = self.get.user_id
        )

        return Response(format_body(1, 'Success', {
            'intro': activity_intro,
            'logs': activity_kan_jia_logs,
            'owner': owner_info,
            'current_user': {
                'is_subscribe': is_subscribe,
                'sharing_code': current_user.sharing_code,
                'is_join': is_join,
                'is_kj': is_kj,
                'kj_money': kj_money
            }
        }))


class LatestTrack(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        track = ActivityLatestTrack.objects.filter(user_id=self.get.user_id).first()
        if track:
            sharing_code = track.sharing_code
            activity_id = track.activity_id
        else:
            sharing_code = ''
            activity_id = ''
        return Response(format_body(1, 'Success', {
            'sharing_code': sharing_code,
            'activity_id': activity_id
        }))


class GeoCoderParamsView(APIView):
    @raise_general_exception
    def get(self,request):
        import urllib, urllib2, json
        params = dict()
        params['key'] = '7S6BZ-VK5KX-JAY4K-7YD4F-WE7Z3-SYFAC'
        params['location'] = request.GET['latitude'] + ',' + request.GET['longitude']
        url = 'http://apis.map.qq.com/ws/geocoder/v1?' + urllib.urlencode(params)
        response = urllib2.urlopen(urllib2.Request(url))
        return Response(format_body(1, 'Success', json.loads(response.read())))



