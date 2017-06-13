from  rest_framework import serializers

from models import Banner


class BannerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Banner
        fields = ('image',)