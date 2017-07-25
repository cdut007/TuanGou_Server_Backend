# _*_ coding:utf-8 _*_
import os

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
            u'%(initial_text)s: <a href="%(initial_url)s"><img src="%(initial_url)s" width="100" height="100"/></a> '
            u'%(clear_template)s<br />%(input_text)s: %(input)s'
        )


class BannerAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ImageField: {'widget': MyClearableFileInput}
    }


class GoodsGalleryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ImageField: {'widget': MyClearableFileInput}
    }

    def save_model(self, request, obj, form, change):
        super(GoodsGalleryAdmin, self).save_model(request,obj, form,change)
        if obj.is_primary:
            GoodsAdmin.create_thumbnail(obj.image)


class GoodsGalleryInline(admin.TabularInline):
    verbose_name = ''
    verbose_name_plural = ''
    model = GoodsGallery
    extra = 0
    fields = ['image', 'is_primary']
    suit_classes = 'suit-tab suit-tab-gallery'
    formfield_overrides = {
        models.ImageField: {'widget': MyClearableFileInput}
    }


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

    def save_formset(self, request, form, formset, change):
        super(GoodsAdmin, self).save_formset( request, form, formset, change)
        if formset.prefix == 'images':
            for key in formset._object_dict:
                image_item = formset._object_dict[key]
                if image_item.is_primary: self.create_thumbnail(image_item.image)
            for image_item in formset.new_objects:
                if image_item.is_primary: self.create_thumbnail(image_item.image)

    @staticmethod
    def create_thumbnail(image):
        image_origin = image.path
        image_thumbnail = os.path.splitext(image_origin)[0] + '_thumbnail' + os.path.splitext(image_origin)[1]
        if not os.path.exists(image_thumbnail):
            from PIL import Image
            try:
                im = Image.open(image)
                im.thumbnail((230, 230))
                im.save(image_thumbnail, im.format)
            except IOError:
                print("cannot create thumbnail for", image_origin)

admin.site.register(GroupBuy, GroupBuyAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(GoodsClassify)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsGallery, GoodsGalleryAdmin)
admin.site.register(GroupBuyGoods)




