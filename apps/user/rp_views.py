# _*_ coding:utf-8 _*_
import json, time, random
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit
from utils.winxin import WeiXinAPI
from iuser.models import GenericOrder, UserProfile
from models import UnpackRedPacketsLog, WeiXinRpSendLog
from iuser.Authentication import Authentication


class UnpackRpView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        receiver = UserProfile.objects.get(sharing_code=request.data['sharing_code'])
        if receiver.id == self.post.user_id:
            return Response(format_body(21, 'Fail', 'can not your own red packet'))

        can_unpack = UnpackRedPacketsLog.can_unpack(
            receiver=receiver.id,
            group_buying_id=request.data['group_buying_id'],
            unpack_user=self.post.user_id
        )
        if not can_unpack:
            return Response(format_body(20, 'Fail', 'Has record for this receiver&group_buying_id'))

        money = UnpackRedPacketsLog.unpack_one_rp(
            receiver=receiver.id,
            group_buying_id=request.data['group_buying_id'],
            unpack_user=self.post.user_id
        )

        if not money:
            return Response(format_body(19, 'Fail', 'Not have blank red packets yet'))

        return Response(format_body(1, 'Success', {'money': money}))


class RpOneEntriesView(APIView):
    @raise_general_exception
    def get(self, request):
        from rp_sqls import sql_rp_one_entries
        receiver = UserProfile.objects.get(sharing_code=request.GET['sharing_code'])

        cursor = connection.cursor()
        sql_rp_one_entries = sql_rp_one_entries.format(
            _group_buying_id = request.GET['group_buying_id'],
            _receiver = receiver.id
        )
        cursor.execute(sql_rp_one_entries)
        rp_entries =dict_fetch_all(cursor)
        return Response(format_body(1, 'Success', {'rp_entries': rp_entries}))


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
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        # self.send(103,172)
        return Response(format_body(1, 'Success', ''))

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

