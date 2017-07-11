# _*_ coding:utf-8 _*_
from django.contrib import admin
from forms import GroupBuyForm
from models import Banner,GoodsClassify,GroupBuy,Goods, GroupBuyGoods, GoodsGallery
# Register your models here.


class GoodsGalleryInline(admin.TabularInline):
    verbose_name = ''
    verbose_name_plural = ''
    model = GoodsGallery
    extra = 0
    suit_classes = 'suit-tab suit-tab-gallery'


class GroupBuyGoodsInline(admin.TabularInline):
    verbose_name = ''
    verbose_name_plural = ''
    model = GroupBuyGoods
    extra = 0
    suit_classes = 'suit-tab suit-tab-goods'


class GroupBuyAdmin(admin.ModelAdmin):
    form = GroupBuyForm
    list_display = ('title', 'goods_classify', 'start_time', 'end_time', 'add_time')
    inlines = [GroupBuyGoodsInline]

    fieldsets = (
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('title', 'goods_classify','start_time', 'end_time')
        }),
    )
    suit_form_tabs = (('general', 'General'), ('goods', 'Goods'))


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


admin.site.register(GroupBuy, GroupBuyAdmin)
admin.site.register(Banner)
admin.site.register(GoodsClassify)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsGallery)
admin.site.register(GroupBuyGoods)




