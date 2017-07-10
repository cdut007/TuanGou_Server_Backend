# _*_ coding:utf-8 _*_
from django.contrib import admin
from django import forms
from models import Banner,GoodsClassify,GroupBuy,Goods, GroupBuyGoods, GoodsGallery
# Register your models here.


class GoodsGalleryInline(admin.TabularInline):
    model = GoodsGallery
    extra = 0
    suit_classes = 'suit-tab suit-tab-gallery'


class GroupBuyGoodsInline(admin.TabularInline):
    model = GroupBuyGoods
    extra = 0


class GroupBuyGoodsForm(forms.ModelForm):
    class Meta:
        model = GroupBuyGoods
        exclude = ['brief_dec']


class GroupBuyAdmin(admin.ModelAdmin):
    list_display = ('title', 'goods_classify', 'start_time', 'end_time', 'add_time')
    inlines = [GroupBuyGoodsInline]
    # form = GroupBuyGoodsForm
    fieldsets = (
        (u'团购详情', {
            'fields': (('title', 'goods_classify'), ('start_time', 'end_time', 'add_time'))
        }),
    )



class GoodsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [GoodsGalleryInline]
    fieldsets = (
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': (('name'),  ('desc'))
        }),
    )

    suit_form_tabs = (('general', 'General'), ('gallery', 'Gallery'))

    class Media:
        js = (
            '/static/js/kindeditor/kindeditor-all.js',
            '/static/js/kindeditor/lang/zh_CN.js',
            '/static/js/kindeditor/config.js'
        )



admin.site.register(Banner)
# admin.site.register(GoodsClassify)
admin.site.register(GroupBuy, GroupBuyAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GroupBuyGoods)
# admin.site.register(GoodsGallery)
