from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from rest_api.models import User as ApiUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError()
        self.context['user'] = user
        return data


class UserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(min_length=12)

    def validate(self, data):
        email = data.get("email")
        token = data.get("token")
        user = ApiUser.objects.get(email=email)
        token_user = Token.objects.get(key=token)
        if not user:
            raise serializers.ValidationError()
        self.context['user'] = user
        return data
