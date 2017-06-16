from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework_jwt.views import verify_jwt_token

from utils.common import format_body
from Authentication import Authentication
from models import UserProfile
from serializers import UserProfileSerializer
# Create your views here.

class UserDetail(APIView):
    def get(self, request):
        if(not request._request.META.has_key('HTTP_AUTHORIZATION')):
            return  Response(format_body(3, 'Need token', ''))
        token = request._request.META['HTTP_AUTHORIZATION']
        user_id = Authentication.verify_auth_token(token)

        user_profile = UserProfile.objects.get(pk=user_id)
        user_serializer = UserProfileSerializer(user_profile)

        return Response(format_body('1', 'success', {'user_profile': user_serializer.data}))

    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Authentication.generate_auth_token(user.id)
            return Response(format_body(1, 'success', {'token': token}), status=status.HTTP_201_CREATED)
        return Response(format_body(2, serializer.errors, ''), status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        pass

    def delete(self, request, pk):
        pass


class Token(APIView):
    def post(self, request):
        user_id = request.data['user_id']
        token = Authentication.generate_auth_token(user_id)
        return Response(format_body(1, 'success', {'token': token}), status=status.HTTP_201_CREATED)
