# _*_ coding:utf-8 _*_
import os, time, json
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMessage

from ilinkgo.settings import conf
from utils.gen_excel import order_excel
from utils.common import format_body, raise_general_exception, random_str, dict_fetch_all
from utils.winxin import WeiXinAPI
from apps.user.models import MerchantPushLog
from iuser.models import UserProfile
from market.models import GroupBuy
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
        # https://docs.google.com/gview?embedded=true&url=http://www.ailinkgo.com:3000/excel/18502808546_2017-08-01.xlsx
        user_id = self.post.user_id
        group_buying_id = request.data['group_buy_id']

        excel = self.get_order_excel(user_id, group_buying_id)

        if excel['count'] == 0:
            return Response(format_body(17, 'Order Empty', ''))

        if request.data['send_type'] == 'email':
            subject = u"类别（%(classify)s）订单详情" % {
                'classify': excel['group_buying_info'].goods_classify.name
            }
            body = u"类别（%(classify)s）发货时间（预计%(month)s月%(day)s日发货）订单信息表" % {
                'classify': excel['group_buying_info'].goods_classify.name,
                'month': excel['group_buying_info'].ship_time.month,
                'day': excel['group_buying_info'].ship_time.day
            }
            from_email = u'爱邻购 <ilinkgo@ultralinked.com>'
            email_to = request.data['email']
            message = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[email_to],
            )
            message.attach_file(excel['excel_file_path'])
            message.send()
            return Response(format_body(1, 'Success', ''))

        if request.data['send_type'] == 'weixin':
            excel_url = 'https://docs.google.com/gview?embedded=true&url=' + excel['excel_web_path']
            title = excel['group_buying_info'].goods_classify.name
            return Response(format_body(1, 'Success', {'excel_url': excel_url, 'title': title}))

        else:
            return Response(format_body(1, 'Success', ''))

    @staticmethod
    def get_order_excel(user_id, group_buying_id):
        from sqls import sql_order_consumer_detail, sql_order_supplier_summary, sql_is_order_empty

        user_info = UserProfile.objects.get(id=user_id)
        group_buying = GroupBuy.objects.get(id=group_buying_id)

        # 先判断订单是否为空
        cursor = connection.cursor()
        sql_is_order_empty = sql_is_order_empty.format(
            _group_buying_id = group_buying_id,
            _merchant_code = user_info.merchant_code
        )
        cursor.execute(sql_is_order_empty)
        count = cursor.fetchone()
        if int(count[0]) == 0:
            return {'count': 0}

        # 查询是否有发送记录
        send_record = MerchantPushLog.objects.filter(
            group_buying_id=group_buying_id,
            merchant_id=user_id,
            is_send_excel=1
        ).first()

        if send_record:
            _excel_file_path = conf.excel_file_path + send_record.excel_path
            _excel_web_path = conf.excel_url_prefix + send_record.excel_path
        else:
            excel_name = str(int(time.time())) + '_' + random_str(4) + '.xls'
            file_path = conf.excel_file_path + excel_name

            sql_order_consumer_detail = sql_order_consumer_detail % {
                'agent_code': user_info.merchant_code,
                'group_buy_id': group_buying_id
            }
            cursor.execute(sql_order_consumer_detail)
            order_list = dict_fetch_all(cursor)
            for item in order_list:
                item['goods_list'] = json.loads(item['goods_list'])

            sql_order_supplier_summary = sql_order_supplier_summary % {
                'agent_code': user_info.merchant_code,
                'group_buy_id': group_buying_id
            }
            cursor.execute(sql_order_supplier_summary)
            ship_list = dict_fetch_all(cursor)

            data = {
                'agent_info': {
                    'time': group_buying.ship_time.strftime('%Y/%m/%d'),
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
                group_buying_id=group_buying_id,
                merchant_id=user_id,
                excel_path=excel_name
            )
            _excel_file_path = file_path
            _excel_web_path = conf.excel_url_prefix + excel_name

        return {
            'count': count[0],
            'excel_file_path': _excel_file_path,
            'excel_web_path': _excel_web_path,
            'group_buying_info': group_buying
        }


class SendWxRedPacketView(APIView):
    def post(self, request):
        wei_xin_api = WeiXinAPI()
        res = wei_xin_api.send_red_pack()
        return Response(format_body(1, 'Success', {'res': res}))
