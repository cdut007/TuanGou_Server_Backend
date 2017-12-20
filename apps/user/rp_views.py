# _*_ coding:utf-8 _*_
import json, time, random
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit
from utils.winxin import WeiXinAPI
from iuser.models import GenericOrder, UserProfile
from models import UnpackRedPacketsLog
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

