# _*_ coding:utf-8 _*_
import os, time, json
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMessage

from utils.gen_excel import order_excel
from utils.common import format_body, raise_general_exception, random_str, dict_fetch_all
from utils.winxin import WeiXinAPI
from ilinkgo.config import image_path, excel_save_base_path

from utils.common import random_str

from iuser.Authentication import Authentication


class WeiXinJsSdkConfigView(APIView):
    @raise_general_exception
    def get(self, request):
        wei_xin_api = WeiXinAPI()

        url = request.GET['url']
        config = wei_xin_api.get_wei_xin_js_sdk_config(url)

        if config == 'error':
            return Response(format_body(15, 'Fail', 'error'))
        return Response(format_body(1, 'Success', config))


class SendOrderInfoView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from apps.user.models import MerchantPushLog
        from iuser.models import UserProfile
        from market.models import GroupBuy
        from sqls import sql1, sql2

        # https://docs.google.com/gview?embedded=true&url=http://www.ailinkgo.com:3000/excel/18502808546_2017-08-01.xlsx
        user_id = self.post.user_id
        group_buy_id = request.data['group_buy_id']

        user_info = UserProfile.objects.get(id=user_id)
        group_buy = GroupBuy.objects.get(id=group_buy_id)
        send_record = MerchantPushLog.objects.filter(
            group_buying_id=group_buy_id,
            merchant_id=user_id,
            is_send_excel=1
        )

        if send_record:
            _file = excel_save_base_path() + send_record[0].excel_path
        else:
            excel_name = str(int(time.time())) + '_' + random_str(4) + '.xlsx'
            file_path = excel_save_base_path() + excel_name

            cursor = connection.cursor()

            sql1 = sql1 % {'agent_code': user_info.openid, 'group_buy_id': group_buy_id}
            cursor.execute(sql1)
            order_list = dict_fetch_all(cursor)

            if not order_list:
                return Response(format_body(17, 'Generic order empty', ''))

            sql2 = sql2 % {'agent_code': user_info.openid, 'group_buy_id': group_buy_id}
            cursor.execute(sql2)
            ship_list = dict_fetch_all(cursor)

            data = {
                'agent_info': {
                    'time': group_buy.ship_time.strftime('%Y/%m/%d'),
                    'address': user_info.address,
                    'phone': user_info.phone_num,
                    'wx': user_info.nickname
                },
                'ship_list': ship_list,
                'order_list': order_list,
                'file_path': file_path
            }
            order_excel(data)
            MerchantPushLog.insert_send_excel_log(
                group_buying_id=group_buy_id,
                merchant_id=user_id,
                excel_path=excel_name
            )
            _file = file_path

        if request.data['send_type'] == 'email':
            subject = u"类别（%(classify)s）订单详情" % {
                'classify': group_buy.goods_classify.name
            }
            body = u"类别（%(classify)s）发货时间（预计%(month)s月%(day)s日发货）订单信息表" % {
                'classify': group_buy.goods_classify.name,
                'month': group_buy.ship_time.month,
                'day': group_buy.ship_time.day
            }
            from_email = u'爱邻购 <ilinkgo@ultralinked.com>'
            email_to = request.data['email']
            message = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[email_to],
            )
            message.attach_file(_file)
            message.send()
            return Response(format_body(1, 'Success', ''))

        if request.data['send_type'] == 'weixin':
            excel_url = 'https://docs.google.com/gview?embedded=true&url=' + 'www.ailinkgo.com/admin/excels/' + send_record[0].excel_path
            title = group_buy.title
            return Response(format_body(1, 'Success', {'excel_url': excel_url, 'title': title}))

        else:
            return Response(format_body(1, 'Success', ''))

