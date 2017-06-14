from  rest_framework import serializers

from models import Banner, GoodsClassify, GroupBuy, Goods, GroupBuyGoods, GoodsGallery


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('image',)


class GoodsClassifySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsClassify
        fields = ('name',)


class GroupBuySerializer(serializers.ModelSerializer):
    goods_classify = serializers.ReadOnlyField(source='GoodsClassify.name')
    
    class Meta:
        model = GroupBuy
        fields = ('goods_classify','start_time','end_time')


class GoodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goods
        fields = ('name',)


class GroupBuyGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBuyGoods
        fields = ('group_buy','goods', 'price')


class GoodsGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsGallery
        fields = ('goods', 'image', 'is_primary', 'add_time')