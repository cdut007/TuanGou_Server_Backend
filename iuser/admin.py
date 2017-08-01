# _*_ coding:utf-8 _*_
from django.db import models
from django.forms import widgets
from django.contrib import admin
from suit.widgets import SuitSplitDateTimeWidget

from models import UserProfile, AgentOrder, GroupBuyGoods
# Register your models here.


class MyCheckBoxInputWidget(widgets.CheckboxInput):
    def render(self, name, value, attrs=None):
        html = super(MyCheckBoxInputWidget, self).render(name, value, attrs)
        html += '<label class={} for={}></label>'.format('tgl-btn', attrs['id'])
        return html


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'sex', 'province', 'city', 'is_agent')
    search_fields = ('nickname',)
    exclude = ('openid', 'unionid', 'privilege')
    readonly_fields = ('nickname', 'sex', 'province', 'city', 'country',
                       'headimgurl', 'address', 'phone_num', 'join_time')
    actions = None
    formfield_overrides = {
        models.DateTimeField: {'widget': SuitSplitDateTimeWidget},
        models.BooleanField: {'widget': MyCheckBoxInputWidget(
            attrs={'class': 'tgl tgl-ios', 'style': 'display:none'}
        )}
    }

    class Media:
        css = {
            "all": ('/static/css/switch.css',)
        }


class AgentOrderAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'group_buy', 'add_time')
    search_fields = ('user__nickname', 'group_buy__title')
    actions = None

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        render_change_form = super(AgentOrderAdmin, self).changeform_view(request, object_id, form_url, extra_context)
        if object_id:
            from django.db import connection
            from utils.common import dict_fetch_all
            from sql import sql1, sql2, sql1_desc, sql2_desc, sql3

            this_generic_order = render_change_form.context_data['original']
            agent_code = this_generic_order.user.openid
            group_buy_id = this_generic_order.group_buy_id

            #sql1
            cursor = connection.cursor()
            sql1 = sql1 % {'agent_code': agent_code, 'group_buy_id': group_buy_id}
            cursor.execute(sql1)
            order_list = dict_fetch_all(cursor)

            render_change_form.context_data['order_list_desc'] = sql1_desc
            render_change_form.context_data['order_list'] = order_list

            #sql2
            sql2 = sql2 % {'agent_code': agent_code, 'group_buy_id': group_buy_id}
            cursor.execute(sql2)
            ship_list = dict_fetch_all(cursor)

            render_change_form.context_data['ship_list_desc'] = sql2_desc
            render_change_form.context_data['ship_list'] = ship_list

            #sql3
            sql3 = sql3 % {'agent_order_id': object_id}
            cursor.execute(sql3)
            group_buy_info = dict_fetch_all(cursor)

            render_change_form.context_data['group_buy_info'] = group_buy_info[0] or []

        return render_change_form


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AgentOrder, AgentOrderAdmin)

