# _*_ coding:utf-8 _*_
import json, time, uuid, functools
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit, virtual_login
from utils.common import decimal_2
from utils.winxin import WeiXinAPI
from ilinkgo.config import image_path
from market.models import GroupBuyGoods, GroupBuy
from iuser.models import GenericOrder, UserProfile
from models import UnpackRedPacketsLog
from  MySQLdb import escape_string

from iuser.Authentication import Authentication

class UserLoginFromAppView(APIView):
    @raise_general_exception
    @virtual_login
    def post(self, request):
        user_id = self.save_wei_xin_user(request.data, 'app')
        token = Authentication.generate_auth_token(user_id)
        return Response(format_body(1, 'Success', {'token': token}))

    @staticmethod
    def save_wei_xin_user(info, login_from, join_way=1):
        record = UserProfile.objects.filter(unionid=info['unionid']).first()
        if record:
            user = record
        else:
            user = UserProfile()
            user.unionid = info['unionid']
            user.sex = info['sex']
            user.province = info['province']
            user.city = info['city']
            user.country = info['country']
            user.privilege = info['privilege']
            user.join_way = join_way

        user.nickname = info['nickname']
        user.headimgurl = info['headimgurl']

        if login_from == 'app' and not user.openid_app:
            user.openid_app = info['openid']
        elif login_from == 'web' and not  user.openid_web:
            user.openid_web = info['openid']
        user.save()
        return user.id


class UserLoginFromWebView(APIView):
    @raise_general_exception
    def get(self,request):
        wei_xin= WeiXinAPI()
        authorization_info = wei_xin.website_authorization_access_token(request.GET['code'])
        user_info = wei_xin.website_user_info(authorization_info['access_token'], authorization_info['openid'])

        user_id = UserLoginFromAppView.save_wei_xin_user(user_info, 'web')
        token = Authentication.generate_auth_token(user_id)
        return Response(format_body(1, 'Success', {'token': token}))


class UserInfoView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        user = UserProfile.objects.get(pk=self.get.user_id)
        data = {
            'nickname': user.nickname,
            'headimgurl': user.headimgurl,
            'address_set': {
                'address': user.address,
                'phone_num': user.phone_num
            },
            'agent_url': 'http://www.ailinkgo.com/?agent_code=' + user.merchant_code,
            'role': 'merchant' if user.is_agent else 'consumer'
        }

        return Response(format_body(1, 'Success', {'user_profile': data}))


class MerchantInfoView(APIView):
    @raise_general_exception
    def get(self, request):
        user = UserProfile.objects.get(merchant_code=request.GET['merchant_code'])
        data = {
            'nickname': user.nickname,
            'headimgurl': user.headimgurl,
            'address': user.address,
        }

        return Response(format_body(1, 'Success', {'merchant_profile': data}))


class UserSharingCodeView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        user = UserProfile.objects.get(pk=self.get.user_id)
        if not user.sharing_code:
            user.sharing_code = uuid.uuid3(uuid.NAMESPACE_DNS, 'SharingCode')
        user.save()

        return Response(format_body(1, 'Success', {'sharing_code': user.sharing_code}))


class ConsumerOrderView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_get_consumer_order

        if request.GET['group_buy_is_over'] == '1':
            is_end = " AND (e.end_time < NOW() OR agent_order.mc_end=1) "
        else:
            is_end = " AND e.end_time > NOW() AND agent_order.mc_end=0 "

        merchant = UserProfile.objects.get(openid=request.GET['merchant_code'])

        sql_get_consumer_order = sql_get_consumer_order % {
            'consumer_id': self.get.user_id,
            'merchant_id': merchant.id,
            'merchant_code': request.GET['merchant_code'],
            'image_prefix': image_path(),
            '_is_end': is_end
        }

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_get_consumer_order)

        data = dict_fetch_all(cursor)

        for item in data:
            item['goods_list'] = json.loads(item['goods_list'])

        return Response(format_body(1, 'Success', {'group_buy': data}))

    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from sqls import sql_create_consumer_order, sql_done_consumer_order_update_stock
        from sqls import sql_create_consumer_order_remarks, sql_is_order_has_red_packets

        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")

        goods_ids = ','.join([str(item['goods_id']) for item in request.data['goods_list']])

        # 插入订单
        insert_values = ""
        for goods_item in request.data['goods_list']:
            if int(goods_item['goods_quantity']) <= 0:
                continue
            insert_values += "('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}),\n".format(
                request.data['merchant_code'],
                datetime.now(),
                self.post.user_id,
                goods_item['goods_id'],
                goods_item['goods_quantity'],
                1,
                request.data['anonymity']
            )
        sql_create_consumer_order = sql_create_consumer_order % {'values': insert_values[0:-2]}
        cursor.execute(sql_create_consumer_order)

        # 添加备注
        if request.data.has_key('remarks') and len(request.data['remarks']) > 0:
            insert_values = ""
            for remark in request.data['remarks']:
                insert_values += "('{group_buying_id}', '{user_id}', '{merchant_code}', '{remark}', '{add_time}'),\n".format(
                    group_buying_id = remark['group_buying_id'],
                    user_id = self.post.user_id,
                    merchant_code = request.data['merchant_code'],
                    remark = escape_string(remark['remark']),
                    add_time = datetime.now()
                )
            sql_create_consumer_order_remarks = sql_create_consumer_order_remarks % {'values': insert_values[0:-2]}
            cursor.execute(sql_create_consumer_order_remarks)

        # 清空购物车
        if request.data['clear_cart'] is True:
            from sqls import sql_clear_cart
            goods_ids = ''
            for item in request.data['goods_list']:
                goods_ids += str(item['goods_id']) + ','
            goods_ids = goods_ids.strip(',')
            sql_clear_cart = sql_clear_cart % {
                'consumer_id':  self.post.user_id,
                'merchant_code': request.data['merchant_code'],
                'goods_ids': goods_ids
            }
            cursor.execute(sql_clear_cart)

        #减少库存
        goods_id = 0
        try:
            for item in request.data['goods_list']:
                goods_id = item['goods_id']
                sql_reduce_stock = sql_done_consumer_order_update_stock.format(
                    item['goods_quantity'],
                    item['goods_id']
                )
                cursor.execute(sql_reduce_stock)
        except OperationalError as e:
            if e.args[0] == 1690:
                this_goods_current_stock = GroupBuyGoods.objects.get(pk=goods_id).stock
                return Response(format_body(12, 'Stock out of range', {'goods_id': goods_id, 'current_stock': this_goods_current_stock}))
            return Response(format_body(11, 'Mysql error', e.message))

        cursor.execute("COMMIT;")

        # 给团长发送微信通知
        try:
            merchant = UserProfile.objects.filter(merchant_code=request.data['merchant_code']).first()
            consumer = UserProfile.objects.get(pk=self.post.user_id)
            sql_get_goods = """
            SELECT
                b.`name`
            FROM
                market_groupbuygoods AS a
            LEFT JOIN market_goods AS b ON a.goods_id=b.id
            WHERE
                a.id = {_goods_id}
            """.format(_goods_id=request.data['goods_list'][0]['goods_id'])
            cursor.execute(sql_get_goods)
            goods_name = dict_fetch_all(cursor)
            goods_name = goods_name[0]['name'] if len(request.data['goods_list'])==1 else str(goods_name[0]['name'])+'等'
            data = {
                "touser": merchant.openid_web,
                "template_id": "gvE4aH7C9LD51v1VkgQ98jlKWec5VLxk1cxnYN6LGl4",
                "data": {
                    "first": {
                        "value": "团员购买通知",
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": goods_name,
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": consumer.nickname,
                        "color": "#173177"
                    },
                    "remark": {
                        "value": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                        "color": "#173177"
                    }
                }
            }
            wei_xin = WeiXinAPI()
            wei_xin.push_notice(data)
        except Exception as e:
            pass

        # 奖励红包
        sql_is_order_has_red_packets = sql_is_order_has_red_packets.format(_goods_ids=goods_ids)
        cursor.execute(sql_is_order_has_red_packets)
        grp = dict_fetch_all(cursor)
        award_red_packets = 1 if grp else 0
        if award_red_packets:
            for item in grp:
                UnpackRedPacketsLog.gen_four_record(receiver=self.post.user_id, group_buying_id=item['group_buying_id'])

        # #一条group_buying_id
        group_buy_goods = GroupBuyGoods.objects.get(pk=request.data['goods_list'][0]['goods_id'])

        return Response(format_body(1, 'Success', {'id': group_buy_goods.group_buy_id, 'award_red_packets': award_red_packets}))

    @raise_general_exception
    @Authentication.token_required
    def delete(self, request):
        # 删除订单
        order_goods = GenericOrder.objects.get(pk=request.GET['order_id'])
        order_goods.delete()

        #更新库存
        order_goods.goods.stock += order_goods.quantity
        order_goods.goods.save()

        return Response(format_body(1, 'Success', ''))


class MerchantOrderView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self,request):

        if request.GET['option'] == 'order_brief':
            return Response(format_body(1, 'Success', ''))

        elif request.GET['option'] == 'order_detail':
            from sqls import sql_merchant_order_detail

            sql_merchant_order_detail = sql_merchant_order_detail % {
                'merchant_code': request.GET['merchant_code'],
                'group_buy_id': request.GET['group_buy_id']
            }

            cursor = connection.cursor()
            cursor.execute("SET SESSION group_concat_max_len = 204800;")
            cursor.execute(sql_merchant_order_detail)
            data = dict_fetch_all(cursor)

            all_quantity = 0; all_amount=0
            for item in data:
                all_quantity += int(item['total_quantity'])
                all_amount += float(item['total_amount'])
                item['goods_list'] = json.loads(item['goods_list'])

            return Response(format_body(1, 'Success', {
                'order_detail': data,
                'summary': {
                    'all_quantity': all_quantity,
                    'all_amount': decimal_2(all_amount)
                }
            }))

        else:
            return Response(format_body(13, 'No this option', ''))


class ShareGroupBuyingView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_share_latest_groupbuying

        sql_share_latest_groupbuying = sql_share_latest_groupbuying.format(
            image_prefix=image_path(),
            user_id=self.get.user_id
        )

        cursor = connection.cursor()
        cursor.execute(sql_share_latest_groupbuying)
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'success', data))


class UserGroupBuyingView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_user_group_buying

        sql_user_group_buying = sql_user_group_buying.format(
            user_id=self.get.user_id,
            image_prefix=image_path(),
            _limit=sql_limit(request)
        )

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_user_group_buying)
        data = dict_fetch_all(cursor)

        for item in data:
            item['images'] = json.loads(item['images'])

        return Response(format_body(1, 'Success', {'group_buying_list': data}))


class MerchantNoticeConsumerTakeGoodsView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from sqls import sql_merchant_notice_consumer_take_goods
        from models import MerchantPushLog
        cursor = connection.cursor()

        sql_notice = sql_merchant_notice_consumer_take_goods.format(
            user_id=self.post.user_id,
            group_buying_id=request.data['group_buy_id']
        )
        cursor.execute(sql_notice)
        users = dict_fetch_all(cursor)

        for user in users:
            data = {
                "touser": user['openid_web'],
                "template_id": "2VIBzyWPhU8tmUr0YT3oWtff-kY6jN8VhRWod22OpjE",
                "data": {
                    "first": {
                        "value": "【爱邻购】亲，你买的商品已经到达团长家了，请尽快联系团长把它领回家哦！\n",
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": (user['goods'][:15]+"..."+"\n") if len(user['goods']) > 15  else  (user['goods']+"\n"),
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "",
                        "color": "#173177"
                    }
                }
            }
            wei_xin = WeiXinAPI()
            wei_xin.push_notice(data)

        MerchantPushLog.insert_send_take_goods_notification(
            group_buying_id=request.data['group_buy_id'],
            merchant_id=self.post.user_id,
        )

        return Response(format_body(1, 'Success', ''))


class MerchantMcEnd(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from iuser.models import AgentOrder

        order = AgentOrder.objects.get(
            user_id=self.post.user_id,
            group_buy_id=request.data['group_buying_id']
        )
        order.mc_end = 1
        order.save()
        return Response(format_body(1, 'Success', ''))


class MerchantShareJieLong(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_merchant_share_jie_long
        cursor = connection.cursor()

        sql_merchant_share_jie_long = sql_merchant_share_jie_long.format(
            _user_id = self.get.user_id,
            _image_prefix = image_path(),
            _limit = sql_limit(request)
        )
        cursor.execute(sql_merchant_share_jie_long)
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', data))


class MerchantCheckJieLongDoing(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_merchant_check_jie_long_doing
        cursor = connection.cursor()

        cursor.execute("SET SESSION group_concat_max_len = 20480;")
        merchant = UserProfile.objects.get(pk=self.get.user_id)
        sql_merchant_check_jie_long = sql_merchant_check_jie_long_doing % {
            '_merchant_id': self.get.user_id,
            '_merchant_code': merchant.merchant_code,
            '_image_prefix': image_path()
        }
        cursor.execute(sql_merchant_check_jie_long)
        data = dict_fetch_all(cursor)

        for item in data:
            if item['headimages']:
                item['headimages'] = json.loads(item['headimages'])
            else:
                item['headimages'] = []

        return Response(format_body(1, 'Success', data))


class MerchantCheckJieLongDone(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_merchant_check_jie_long_done
        cursor = connection.cursor()

        cursor.execute("SET SESSION group_concat_max_len = 20480;")
        merchant = UserProfile.objects.get(pk=self.get.user_id)
        sql_merchant_check_jie_long = sql_merchant_check_jie_long_done % {
            '_merchant_id': self.get.user_id,
            '_merchant_code': merchant.merchant_code,
            '_image_prefix': image_path(),
            '_limit': sql_limit(request)
        }
        cursor.execute(sql_merchant_check_jie_long)
        data = dict_fetch_all(cursor)

        for item in data:
            if item['headimages']:
                item['headimages'] = json.loads(item['headimages'])
            else:
                item['headimages'] = []

        return Response(format_body(1, 'Success', data))


class MerchantJieLongConsView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_merchant_jie_long_purchased_user
        cursor = connection.cursor()

        cursor.execute("SET SESSION group_concat_max_len = 20480;")
        merchant = UserProfile.objects.filter(merchant_code=request.GET['merchant_code']).first()
        sql_merchant_jie_long_purchased_user = sql_merchant_jie_long_purchased_user % {
            '_merchant_code': merchant.merchant_code,
            '_merchant_id': merchant.id,
            '_limit': sql_limit(request)
        }
        cursor.execute(sql_merchant_jie_long_purchased_user)
        data = dict_fetch_all(cursor)

        for item in data:
            item['goods_list'] = json.loads(item['goods_list'])

        return Response(format_body(1, 'Success', data))


class GetConsumerOrderView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_consumer_order_web
        cursor = connection.cursor()

        if request.GET['status'] == 'done':
            _doing_or_done = ' d.mc_end=1 OR e.end_time < NOW() OR e.on_sale=0 '
            _limit = sql_limit(request)
        else:
            _doing_or_done = ' d.mc_end=0 AND e.end_time > NOW() AND e.on_sale=1'
            _limit = ''

        cursor.execute("SET SESSION group_concat_max_len = 20480;")
        sql_consumer_order_web = sql_consumer_order_web % {
            '_image_prefix': image_path(),
            '_doing_or_done': _doing_or_done,
            '_consumer_id': self.get.user_id,
            '_limit': _limit
        }
        cursor.execute(sql_consumer_order_web)
        data = dict_fetch_all(cursor)

        for item in data:
            if item['consumers']:
                item['consumers'] = json.loads(item['consumers'])
            else:
                item['consumers'] = []

        return Response(format_body(1, 'Success', data))


class ConsumerOrderDetailView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_consumer_order_detail
        cursor = connection.cursor()

        cursor.execute("SET SESSION group_concat_max_len = 20480;")
        sql_consumer_order_detail = sql_consumer_order_detail % {
            '_image_prefix': image_path(),
            '_group_buying_id': request.GET['group_buying_id'],
            '_merchant_code': request.GET['merchant_code'],
            '_consumer_id': self.get.user_id
        }
        cursor.execute(sql_consumer_order_detail)
        data = dict_fetch_all(cursor)

        for item in data:
            item['goods_list'] = json.loads(item['goods_list'])

        data = data[0] if data else {}

        return Response(format_body(1, 'Success', data))


class ConsumerOrderErtView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_consumer_order_ert
        cursor = connection.cursor()

        cursor.execute("SET SESSION group_concat_max_len = 20480;")
        sql_consumer_order_ert = sql_consumer_order_ert % {
            '_merchant_code': request.GET['merchant_code'],
            '_group_buying_id': request.GET['group_buying_id'],
            '_limit': sql_limit(request)
        }
        cursor.execute(sql_consumer_order_ert)
        data = dict_fetch_all(cursor)

        for item in data:
            item['goods_list'] = json.loads(item['goods_list'])

        return Response(format_body(1, 'Success', data))









