# _*_ coding:utf-8 _*_
from django.contrib import admin
from django.forms import widgets
from django.db import models
from forms import GroupBuyForm
from models import Banner,GoodsClassify,GroupBuy,Goods, GroupBuyGoods, GoodsGallery
# Register your models here.


class MyClearableFileInput(widgets.ClearableFileInput):
    def __init__(self):
        super(MyClearableFileInput, self).__init__()
        self.template_with_initial = (
            '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> '
            '%(clear_template)s<br />%(input_text)s: %(input)s'
        )

    def render(self, name, value, attrs=None):
        html = super(MyClearableFileInput, self).render(name, value, attrs)
        return html


class GoodsGalleryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ImageField: {'widget': MyClearableFileInput}
    }


class GoodsGalleryInline(admin.TabularInline):
    verbose_name = ''
    verbose_name_plural = ''
    model = GoodsGallery
    extra = 0
    fields = ['image', 'is_primary']
    suit_classes = 'suit-tab suit-tab-gallery'


class GroupBuyGoodsInline(admin.TabularInline):
    verbose_name = ''
    verbose_name_plural = ''
    model = GroupBuyGoods
    extra = 0
    suit_classes = 'suit-tab suit-tab-goods'


class GroupBuyAdmin(admin.ModelAdmin):
    form = GroupBuyForm
    list_display = ('title', 'goods_classify', 'is_end')
    inlines = [GroupBuyGoodsInline]

    fieldsets = (
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('title', 'goods_classify', 'end_time','ship_time')
        }),
    )
    suit_form_tabs = (('general', 'General'), ('goods', 'Goods'))

    class Media:
        css = {
            "all": ('/static/js/chosen.jquery/chosen.css',)
        }
        js = (
            '/static/js/chosen.jquery/chosen.jquery.js',
            '/static/js/chosen.jquery/config.js'
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


admin.site.register(GroupBuy, GroupBuyAdmin)
admin.site.register(Banner)
admin.site.register(GoodsClassify)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsGallery, GoodsGalleryAdmin)
admin.site.register(GroupBuyGoods)




