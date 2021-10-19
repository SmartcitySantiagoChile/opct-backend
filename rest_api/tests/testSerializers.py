from django.test import TestCase
from rest_framework import serializers

from django.contrib.auth.models import User
from rest_api.serializers import UserLoginSerializer


class UserLoginSerializerTest(TestCase):

    def test_missing_user_name(self):
        data = {}
        user = UserLoginSerializer()
        self.assertRaises(serializers.ValidationError, user.validate, data)
