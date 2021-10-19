import json

from django.urls import reverse
from rest_framework.test import (APITestCase, APIClient)


class LoginTest(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.request_url = reverse('login')

    def test_basic_login(self):
        response = self.client.post(self.request_url)
        print(json.loads(response.content))
