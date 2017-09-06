from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all
from sql import sql_copy_group_buy, sql_copy_group_buy_goods

class GroupBuyAdminView(APIView):
    def post(self, request):
        option = request.data['option']
        params = request.data['params']

        if option == 'copy':
            from sql import sql_copy_group_buy_goods, sql_copy_group_buy

            cursor = connection.cursor()

            # new group buy
            group_buy_id = params['group_buy_id']
            sql_copy_group_buy = sql_copy_group_buy .format(group_buy_id)
            cursor.execute(sql_copy_group_buy)

            # get the new group buy id
            cursor.execute("SELECT LAST_INSERT_ID() AS new_group_buy_id;")
            new_group_buy_id = cursor.fetchone()[0]

            # create new group buy goods
            sql_copy_group_buy_goods = sql_copy_group_buy_goods.format(new_group_buy_id, group_buy_id)
            cursor.execute(sql_copy_group_buy_goods)

            return Response(format_body(1, 'Success', {"new_group_buy_id": new_group_buy_id}))

        return Response(format_body(10, 'No this option', ''))