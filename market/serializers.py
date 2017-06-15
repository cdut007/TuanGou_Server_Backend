from  rest_framework import serializers

from models import Banner, GoodsClassify, GroupBuy, Goods, GroupBuyGoods, GoodsGallery
from ilinkgo.dbConfig import image_path


class GoodsGallerySerializer(serializers.Serializer):
   image = serializers.ImageField()

   # def get_fields(self):
   #     self.image = '123' + self.image
   #     super(GoodsClassifySerializer,  self).get_fields()


class GoodsSerializer(serializers.ModelSerializer):
    images = GoodsGallerySerializer(many=True, read_only=True)
    class Meta:
        model = Goods
        fields = ('name','images')


class GoodsClassifySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsClassify
        fields = ('name', 'desc', 'icon', 'image')


class GroupBuyGoodsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    goods = GoodsSerializer(read_only=True)
    price = serializers.FloatField()
    stock = serializers.IntegerField()
    brief_dec = serializers.CharField()


class GroupBuySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title =  serializers.CharField(required=True, max_length=64)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

