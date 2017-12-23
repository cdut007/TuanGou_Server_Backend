# _*_ coding:utf-8 _*_
import json, time, random, pika
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit
from utils.winxin import WeiXinAPI
from iuser.models import GenericOrder, UserProfile, AgentOrder
from models import UnpackRedPacketsLog, WeiXinRpSendLog
from iuser.Authentication import Authentication


class UnpackRpView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        receiver = UserProfile.objects.get(sharing_code=request.data['sharing_code'])

        #不能拆自己的红包
        if receiver.id == self.post.user_id:
            return Response(format_body(21, 'Fail', u'您不能拆自己的红包哦！'))

        # 已经帮这位好友拆过
        can_unpack = UnpackRedPacketsLog.can_unpack(
            receiver=receiver.id,
            group_buying_id=request.data['group_buying_id'],
            unpack_user=self.post.user_id
        )
        if not can_unpack:
            return Response(format_body(20, 'Fail', u'您已经帮这位好友拆过这个红包了哦！'))

        # 今天拆的次数有没3次
        times_today = UnpackRedPacketsLog.times_today(unpack_user=self.post.user_id)
        if times_today >= 3:
            return Response(format_body(23, 'Fail', u'您今天已经帮好友拆过3次红包了哦！'))

        # 如果没有money, 说明四个红包都已拆完
        money = UnpackRedPacketsLog.unpack_one_rp(
            receiver=receiver.id,
            group_buying_id=request.data['group_buying_id'],
            unpack_user=self.post.user_id
        )
        if not money:
            return Response(format_body(19, 'Fail', u'四个红包已经全部拆完了哦！'))

        return Response(format_body(1, 'Success', {'money': money}))


class RpOneEntriesView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from rp_sqls import sql_rp_one_entries

        receiver = UserProfile.objects.get(sharing_code=request.GET['sharing_code'])

        rp = UnpackRedPacketsLog.objects.filter(
            receiver = receiver.id,
            group_buying_id = request.GET['group_buying_id']
        ).first()
        merchant = UserProfile.objects.get(pk=rp.get_from)

        # access_user = Authentication.access_user(request)
        # if not access_user == receiver.id:
        #     # 红包链接是否还有效
        #     remain_order = GenericOrder.objects.filter(
        #             user_id = receiver.id,
        #             goods__group_buy_id = request.GET['group_buying_id']
        #     ).count()
        #     rp = UnpackRedPacketsLog.objects.filter(
        #         receiver = receiver.id,
        #         group_buying_id = request.GET['group_buying_id']
        #     ).first()
        #     merchant_order = AgentOrder.objects.filter(
        #         user_id = rp.get_from,
        #         group_buy_id =  request.GET['group_buying_id']
        #     ).first()
        #     if (not remain_order) or merchant_order.mc_end == 1 or merchant_order.group_buy.end_time < datetime.now():
        #         return Response(format_body(22, 'Fail', u'sorry，该红包已经失效了'))

        cursor = connection.cursor()
        sql_rp_one_entries = sql_rp_one_entries.format(
            _group_buying_id = request.GET['group_buying_id'],
            _receiver = receiver.id
        )
        cursor.execute(sql_rp_one_entries)
        rp_entries = dict_fetch_all(cursor)

        yichai = 0
        for rp in rp_entries:
            if rp['user_id'] == self.get.user_id:
                yichai = 1

        def pop_user_id(v):
            v.pop('user_id')
            return v

        return Response(format_body(1, 'Success', {
            'rp_entries': map(pop_user_id, rp_entries),
            'merchant_code': merchant.merchant_code,
            'yichai': yichai,
            'receiver': {
                'nickname': receiver.nickname,
                'headimgurl': receiver.headimgurl
            }
        }))


class RpUnopenedView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from rp_sqls import sql_unopened_rp

        cursor = connection.cursor()
        sql_unopened_rp = sql_unopened_rp.format(
            _receiver = self.get.user_id
        )
        cursor.execute(sql_unopened_rp)
        rp_unopened =dict_fetch_all(cursor)
        return Response(format_body(1, 'Success', {'rp_unopened': rp_unopened}))


class RpOpenedView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from rp_sqls import sql_opened_rp

        cursor = connection.cursor()
        sql_opened_rp = sql_opened_rp.format(
            _receiver = self.get.user_id
        )
        cursor.execute(sql_opened_rp)
        rp_opened =dict_fetch_all(cursor)
        return Response(format_body(1, 'Success', {'rp_opened': rp_opened}))


class RpFailedView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from rp_sqls import sql_failed_rp

        cursor = connection.cursor()
        sql_failed_rp = sql_failed_rp.format(
            _receiver = self.get.user_id
        )
        cursor.execute(sql_failed_rp)
        rp_failed =dict_fetch_all(cursor)
        return Response(format_body(1, 'Success', {'rp_failed': rp_failed}))


class RpSendView(APIView):
    @raise_general_exception
    def get(self, request):
        # self.send_to_rabbitmq(1,2)
        return Response(format_body(1, 'success', ''))

    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        self.send(request.data['group_buying_id'],request.data['get_from'])
        return Response(format_body(1, 'success', ''))

    @staticmethod
    def send_to_rabbitmq(group_buying_id, get_from):
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = conn.channel()
            channel.queue_declare(queue='send_wei_xin_rp', durable=True)
            data = json.dumps({
                'group_buying_id': group_buying_id,
                'get_from': get_from
            })
            channel.basic_publish(
                exchange='',
                routing_key='send_wei_xin_rp',
                body=data,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
        except Exception:
            RpSendView.send(group_buying_id, get_from)

    @staticmethod
    def send(group_buying_id, get_from):
        from rp_sqls import sql_send_rp
        wei_xin = WeiXinAPI()

        cursor = connection.cursor()
        sql_send_rp = sql_send_rp.format(
            _group_buying_id = group_buying_id,
            _get_from = get_from
        )
        cursor.execute(sql_send_rp)
        receiver_list =dict_fetch_all(cursor)
        for receiver in receiver_list:
            bill_no = WeiXinRpSendLog.gen_bill_no()
            res = wei_xin.send_red_pack(
                money=int(receiver['money']*100),
                open_id=receiver['openid_web'],
                bill_no=bill_no
            )
            send_id = WeiXinRpSendLog.insert_one_log(
                open_id=receiver['openid_web'],
                money=receiver['money'],
                bill_no=bill_no,
                res=res
            )
            if res['result_code'] == 'SUCCESS':
                UnpackRedPacketsLog.update_send(
                    group_buying_id=group_buying_id,
                    receiver=receiver['receiver'],
                    send_id=send_id
                )
        return  True


class RpLogsView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self,request):
        from rp_sqls import sql_rp_logs

        cursor = connection.cursor()
        sql_rp_logs = sql_rp_logs.format(
            _user_id = self.get.user_id
        )
        cursor.execute(sql_rp_logs)
        logs =dict_fetch_all(cursor)
        return Response(format_body(1, 'Success', {'logs': logs}))


class RpSummaryView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from rp_sqls import sql_rp_amount, sql_unopened_and_opened_rp_count, sql_failed_rp_count

        cursor = connection.cursor()
        query = {'_user_id': self.get.user_id}

        cursor.execute(sql_rp_amount.format(**query))
        amount = cursor.fetchone()
        amount = amount[0]

        cursor.execute(sql_unopened_and_opened_rp_count.format(**query))
        opened_and_unopened_count = dict_fetch_all(cursor)
        opened_and_unopened_count = opened_and_unopened_count[0]

        cursor.execute(sql_failed_rp_count.format(**query))
        failed_count = cursor.fetchone()
        failed_count = failed_count[0]

        return Response(format_body(1, 'Success', {
            'rp_amount': amount,
            'rp_opened': opened_and_unopened_count['opened_rp'],
            'rp_unopened': opened_and_unopened_count['unopened_rp'],
            'rp_failed': failed_count
        }))

