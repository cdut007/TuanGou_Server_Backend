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
    list_display = ('nickname', 'sex', 'province', 'city', 'is_agent')
    search_fields = ('nickname',)
    exclude = ('openid', 'unionid', 'privilege')
    readonly_fields = ('nickname', 'sex', 'province', 'city', 'country',
                       'headimgurl', 'address', 'phone_num', 'join_time')
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
    readonly_fields = ('user', 'group_buy', 'goods_ids', 'add_time')
    list_display = ('id','user', 'group_buy', 'add_time')
    search_fields = ('user',)
    actions_selection_counter = True
    date_hierarchy = 'add_time'
    actions = None

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        render_change_form = super(AgentOrderAdmin, self).changeform_view(request, object_id, form_url, extra_context)
        if object_id:
            goods_ids = render_change_form.context_data['original'].goods_ids
            goods_names = ''
            for goods_id in goods_ids.split(','):
                goods = GroupBuyGoods.objects.get(pk=goods_id)
                goods_names += goods.goods.name + u', '
            render_change_form.context_data['original'].goods_ids = goods_names
        return render_change_form

    # class Media:
    #     js = (
    #         '\js\iuser.admin.generic_order.js',
    #     )


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AgentOrder, AgentOrderAdmin)

