from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from rest_api.models import ContractType, Organization


class BaseTestCase(APITestCase):
    fixtures = [
        "contracttypes.json",
        "operationprogramstatuses.json",
        "operationprogramtypes.json",
        "groups.json",
        "grouppermissions.json",
        "changeoprequeststatuses.json",
    ]

    def setUp(self) -> None:
        self.client = APIClient()
        self.create_op_user()
        self.create_organization_user()
        self.create_user_user()
        self.contract_type = ContractType.objects.get(id=1)
        self.create_default_organization()

    def create_op_user(self):
        self.op_user_attributes = {
            "email": "op@opct.com",
            "password": "testpassword1",
            "organization": None,
            "access_to_ops": True,
            "access_to_organizations": False,
            "access_to_users": False,
        }
        self.op_user = get_user_model().objects.create_user(**self.op_user_attributes)

    def create_organization_user(self):
        self.organization_user_attributes = {
            "email": "organization@opct.com",
            "password": "testpassword1",
            "organization": None,
            "access_to_ops": False,
            "access_to_organizations": True,
            "access_to_users": False,
        }
        self.organization_user = get_user_model().objects.create_user(
            **self.organization_user_attributes
        )

    def create_user_user(self):
        self.user_user_attributes = {
            "email": "user@opct.com",
            "password": "testpassword1",
            "organization": None,
            "access_to_ops": False,
            "access_to_organizations": False,
            "access_to_users": True,
        }
        self.user_user = get_user_model().objects.create_user(
            **self.user_user_attributes
        )

    def create_default_organization(self):
        organization_params = {
            "name": "Default",
            "created_at": timezone.now(),
            "contract_type": self.contract_type,
            "default_user_contact": self.user_user,
        }
        self.organization_base = Organization.objects.create(**organization_params)

    def login_op_user(self):
        self.client.logout()
        self.client.login(username="op@opct.com", password="testpassword1")

    def login_user_user(self):
        self.client.logout()
        self.client.login(username="user@opct.com", password="testpassword1")

    def login_organization_user(self):
        self.client.logout()
        self.client.login(username="organization@opct.com", password="testpassword1")
