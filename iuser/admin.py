from django.db import models
from django.forms import widgets
from django.contrib import admin
from suit.widgets import SuitSplitDateTimeWidget

from models import UserProfile
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

admin.site.register(UserProfile, UserProfileAdmin)

