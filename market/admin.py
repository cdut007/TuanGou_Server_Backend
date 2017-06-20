# _*_ coding:utf-8 _*_
from django.contrib import admin
from django import forms
from models import Banner,GoodsClassify,GroupBuy,Goods, GroupBuyGoods, GoodsGallery
# Register your models here.

class GroupBuyGoodsInline(admin.TabularInline):
    model = GroupBuyGoods
    extra = 0

class GroupBuyGoodsForm(forms.ModelForm):
    class Meta:
        model = GroupBuyGoods
        exclude = ['brief_dec']


class GroupBuyAdmin(admin.ModelAdmin):
    list_display = ('title', 'goods_classify', 'start_time', 'end_time', 'add_time')
    # form = GroupBuyGoodsForm
    fieldsets = (
        (u'团购详情', {
            'fields': (('title', 'goods_classify'), ('start_time', 'end_time', 'add_time'))
        }),
    )
    inlines = [GroupBuyGoodsInline]


admin.site.register(Banner)
admin.site.register(GoodsClassify)
admin.site.register(GroupBuy, GroupBuyAdmin)
admin.site.register(Goods)
admin.site.register(GroupBuyGoods)
admin.site.register(GoodsGallery)
