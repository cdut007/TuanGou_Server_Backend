# _*_ coding:utf-8 _*_
import os, time, json
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from ilinkgo.settings import conf
from utils.common import format_body, raise_general_exception, random_str, dict_fetch_all
from utils.winxin import WeiXinAPI

from models import ActivityJoin, KanJiaLog
from iuser.Authentication import Authentication
from iuser.models import UserProfile

    
class WxPayView(APIView):
    @raise_general_exception
    def post(self, request):
        wei_xin_api = WeiXinAPI()
        res = wei_xin_api.pay()
        return Response(format_body(1, 'Success', res))


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

        return Response(format_body(1, 'Success', {'intro': activity_intro, 'ranking': activity_ranking}))


class KanJiaDetail(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_activity_detail, sql_activity_user_info, sql_activity_kan_jia_logs
        owner = UserProfile.objects.get(sharing_code=request.GET['sharing_code'])

        cursor = connection.cursor()

        sql_activity_detail = sql_activity_detail.format(activity_id = request.GET['activity_id'],_image_prefix=conf.image_url_prefix)
        cursor.execute(sql_activity_detail)
        activity_intro = dict_fetch_all(cursor)[0]

        sql_activity_user_info = sql_activity_user_info.format(activity_id = request.GET['activity_id'],owner=owner.id)
        cursor.execute(sql_activity_user_info)
        owner_info = dict_fetch_all(cursor)[0]

        sql_activity_kan_jia_logs = sql_activity_kan_jia_logs.format(activity_id = request.GET['activity_id'],owner=owner.id)
        cursor.execute(sql_activity_kan_jia_logs)
        activity_kan_jia_logs = dict_fetch_all(cursor)

        owner_info['is_purchased'] = 0
        owner_info['pickup_code'] = 'MKH938479'

        current_user = UserProfile.objects.get(pk=172)
        wei_xin_api = WeiXinAPI()
        wx_info = wei_xin_api.user_info(current_user.openid_web)

        return Response(format_body(1, 'Success', {
            'intro': activity_intro,
            'logs': activity_kan_jia_logs,
            'owner': owner_info,
            'current_user': {
                'is_subscribe': wx_info['subscribe'] if wx_info.has_key('subscribe') else 0,
                'sharing_code': current_user.sharing_code
            }
        }))



