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
        self.contract_type = ContractType.objects.get(id=1)
        self.organization_contact_user = self.create_user_user(
            "contact@opct.com", "testpassword1"
        )
        self.organization_base = self.create_organization(
            "Default", self.contract_type, self.organization_contact_user
        )
        self.op_user = self.create_op_user("op@opct.com", "testpassword1")
        self.organization_user = self.create_organization_user(
            "organization@opct.com", "testpassword1"
        )
        self.user_user = self.create_user_user("user@opct.com", "testpassword1")

    @staticmethod
    def create_op_user(email, password, organization=None):
        op_user_attributes = {
            "email": email,
            "password": password,
            "organization": organization,
            "access_to_ops": True,
            "access_to_organizations": False,
            "access_to_users": False,
        }
        return get_user_model().objects.create_user(**op_user_attributes)

    @staticmethod
    def create_organization_user(email, password, organization=None):
        organization_user_attributes = {
            "email": email,
            "password": password,
            "organization": organization,
            "access_to_ops": False,
            "access_to_organizations": True,
            "access_to_users": False,
        }
        return get_user_model().objects.create_user(**organization_user_attributes)

    @staticmethod
    def create_user_user(email, password, organization=None):
        user_user_attributes = {
            "email": email,
            "password": password,
            "organization": organization,
            "access_to_ops": False,
            "access_to_organizations": False,
            "access_to_users": True,
        }
        return get_user_model().objects.create_user(**user_user_attributes)

    @staticmethod
    def create_organization(name, contract_type, user_contact):
        organization_params = {
            "name": name,
            "created_at": timezone.now(),
            "contract_type": contract_type,
            "default_user_contact": user_contact,
        }
        return Organization.objects.create(**organization_params)

    def login_op_user(self):
        self.client.logout()
        self.client.login(username="op@opct.com", password="testpassword1")

    def login_user_user(self):
        self.client.logout()
        self.client.login(username="user@opct.com", password="testpassword1")

    def login_organization_user(self):
        self.client.logout()
        self.client.login(username="organization@opct.com", password="testpassword1")
