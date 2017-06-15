from  rest_framework import serializers

from models import Banner, GoodsClassify, GroupBuy, Goods, GroupBuyGoods, GoodsGallery


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('image',)


class GoodsGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsGallery
        fields = ('image',)


class GoodsSerializer(serializers.ModelSerializer):
    images = GoodsGallerySerializer(many=True, read_only=True)
    class Meta:
        model = Goods
        fields = ('name','images')


class GoodsClassifySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsClassify
        fields = ('name',)


class GroupBuyGoodsSerializer(serializers.Serializer):
    goods = GoodsSerializer(read_only=True)
    price = serializers.FloatField()


class GroupBuySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title =  serializers.CharField(required=True, max_length=64)
    goods_classify = serializers.ReadOnlyField(source='goods_classify.name')
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    group_buy_goods = GroupBuyGoodsSerializer(many=True, read_only=True)

