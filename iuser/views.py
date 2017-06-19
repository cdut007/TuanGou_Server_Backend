from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from utils.common import format_body
from models import UserProfile, AgentOrder
from serializers import UserProfileSerializer, UserAddressSerializer,AgentOrderSerializer

from Authentication import Authentication
# Create your views here.


class UserView(APIView):
    @Authentication.token_required
    def get(self, request):
        user_profile = UserProfile.objects.get(pk=self.get.user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(format_body(1, 'Success', {'user_profile': serializer.data}))

    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_record = UserProfile.objects.filter(openid=serializer.validated_data['openid']).first()
            if user_record:
                token = Authentication.generate_auth_token(user_record.id)
                return Response(format_body(1, 'Success', {'token': token}))
            user = serializer.save()
            token = Authentication.generate_auth_token(user.id)
            return Response(format_body(1, 'Success', {'token': token}))
        return Response(format_body(2, 'ErrorParams', serializer.errors))

    @Authentication.token_required
    def put(self,request):
        user = UserProfile.objects.filter(pk=self.put.user_id).first()
        serializer = UserProfileSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            return Response(format_body(1, 'success',''))
        return Response(format_body(2, serializer.errors, ''))

    def delete(self, request, pk):
        pass


class UserAddressView(APIView):
    @Authentication.token_required
    def get(self, request):
        user = UserProfile.objects.get(pk=self.get.user_id)
        if user.phone_num == '' or user.address == '':
            return Response(format_body(5, 'Object does not exist', ''))
        serializer = UserAddressSerializer(user)
        return Response(format_body(1, 'Success', {'user_address': serializer.data}))

    @Authentication.token_required
    def post(self, request):
        user = UserProfile.objects.get(pk=self.post.user_id)
        serializer = UserAddressSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            return Response(format_body(1, 'Success', ''))
        return Response(format_body(2, serializer.errors, ''))


class AgentOrderView(APIView):
    # def get(self, request):


    @Authentication.token_required
    def post(self, request):
        user = UserProfile.objects.get(pk=self.post.user_id)
        if not user.is_agent == 1:
            return Response(format_body(3, 'The user is not agent', ''))

        request.data['user'] = self.post.user_id
        serializer = AgentOrderSerializer(data=request.data)
        if serializer.is_valid():
            order_record = AgentOrder.objects.filter(user=user.id, group_buy=serializer.validated_data['group_buy'])
            if order_record:
                return Response(format_body(4, 'The user already applied this group_buy', ''))
            serializer.save()
            return Response(format_body(1, 'Success', {'agent_url': user.openid}))
        return Response(format_body(2, serializer.errors, ''))