from  rest_framework import serializers

from models import Banner, GoodsClassify, GroupBuy, Goods, GroupBuyGoods, GoodsGallery
from ilinkgo.config import image_path
from utils.common import utc_time_to_local_time

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('image',)

    def to_representation(self, instance):
        data = super(BannerSerializer, self).to_representation(instance)
        data['image'] =  image_path() + data['image']
        return data


class GoodsGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsGallery
        fields = ('image',)

    def to_representation(self, instance):
       data = super(GoodsGallerySerializer, self).to_representation(instance)
       data['image'] = image_path() + data['image']
       return data


class GoodsSerializer(serializers.ModelSerializer):
    images = GoodsGallerySerializer(many=True, read_only=True)

    class Meta:
        model = Goods
        fields = ('name', 'desc', 'images')

    def to_representation(self, instance):
       data = super(GoodsSerializer, self).to_representation(instance)
       if not data['images']:
           data['images'] = [{'image': ''}]
       return data


class GroupBuyGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(read_only=True)

    class Meta:
        model = GroupBuyGoods
        fields = ('id', 'goods', 'price', 'stock', 'brief_dec', 'group_buy')


class GroupBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBuy
        fields = ('id', 'title', 'start_time', 'end_time')

    def to_representation(self, instance):
        data = super(GroupBuySerializer, self).to_representation(instance)
        data['start_time'] = utc_time_to_local_time(data['start_time'])
        data['end_time'] = utc_time_to_local_time(data['end_time'])
        return data


class GoodsClassifySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsClassify
        fields = ('id', 'name', 'desc', 'icon', 'image')

    def to_representation(self, instance):
        path = image_path()
        data = super(GoodsClassifySerializer, self).to_representation(instance)
        data['image'] =  path + data['image']
        data['icon'] = path + data['icon']
        return data


class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField(use_url='images/%Y/%m')


