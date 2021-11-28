import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from rest_api.models import (
    ContractType,
    Organization,
    OperationProgram,
    OperationProgramType,
    ChangeOPRequest,
    ChangeOPRequestStatus,
    CounterPartContact,
    ChangeOPRequestMessage,
)


class BaseTestCase(APITestCase):
    fixtures = [
        "contracttypes.json",
        "operationprogramstatuses.json",
        "operationprogramtypes.json",
        "groups.json",
        "grouppermissions.json",
        "changeoprequeststatuses.json",
    ]

    GET_REQUEST = "get"
    POST_REQUEST = "post"
    PUT_REQUEST = "put"  # update
    PATCH_REQUEST = "patch"  # partial update
    DELETE_REQUEST = "delete"

    def setUp(self) -> None:
        """
        Create contract type, contact user, organization base, op group user, organization group user and
        user group user
        """
        self.client = APIClient()
        self.contract_type = ContractType.objects.get(id=1)

        self.organization_base = self.create_organization("Default", self.contract_type)
        self.organization_contact_user = self.create_user_user(
            "contact@opct.com", "testpassword1", organization=self.organization_base
        )
        CounterPartContact(
            user=self.organization_contact_user,
            organization=self.organization_base,
            counter_part_organization=self.organization_base,
        ).save()
        self.op_user = self.create_op_user("op@opct.com", "testpassword1")
        self.organization_user = self.create_organization_user(
            "organization@opct.com", "testpassword1"
        )
        self.user_user = self.create_user_user("user@opct.com", "testpassword1")

    def _make_request(
        self,
        client,
        method,
        url,
        data,
        status_code,
        json_process=False,
        **additional_method_params,
    ):
        method_obj = None
        if method == self.GET_REQUEST:
            method_obj = client.get
        elif method == self.POST_REQUEST:
            method_obj = client.post
        elif method == self.PATCH_REQUEST:
            method_obj = client.patch
        elif method == self.PUT_REQUEST:
            method_obj = client.put
        elif method == self.DELETE_REQUEST:
            method_obj = client.delete
        response = method_obj(url, data, **additional_method_params)
        if response.status_code != status_code:
            print(f"error {response.status_code}: {response.content}")
            self.assertEqual(response.status_code, status_code)

        if json_process:
            return json.loads(response.content)
        return response

    @staticmethod
    def create_op_user(email, password, organization=None):
        op_user_attributes = {
            "email": email,
            "password": password,
            "organization": organization,
            "access_to_ops": True,
            "access_to_organizations": False,
            "access_to_users": False,
            "role": "Técnico de planificación",
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
            "role": "Técnico de planificación",
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
            "role": "Técnico de planificación",
        }
        return get_user_model().objects.create_user(**user_user_attributes)

    @staticmethod
    def create_organization(name, contract_type):
        organization_params = {
            "name": name,
            "created_at": timezone.now(),
            "contract_type": contract_type,
        }
        return Organization.objects.create(**organization_params)

    @staticmethod
    def create_op(start_at, op_type=1):
        return OperationProgram.objects.create(
            start_at=start_at, op_type=OperationProgramType.objects.get(id=op_type)
        )

    @staticmethod
    def create_change_op_request(
        user,
        op,
        counter_part,
        contract_type,
        status_id=1,
        title="Change OP Request test",
    ):
        params = {
            "created_at": timezone.now(),
            "creator": user,
            "op": op,
            "status": ChangeOPRequestStatus.objects.get(id=status_id),
            "counterpart": counter_part,
            "contract_type": contract_type,
            "title": title,
            "op_release_date": "2030-01-01",
            "reason": "other",
        }
        return ChangeOPRequest.objects.create(**params)

    @staticmethod
    def create_counter_part_contact(organization, user, counter_part_organization):
        return CounterPartContact.objects.create(
            organization=organization,
            user=user,
            counter_part_organization=counter_part_organization,
        )

    @staticmethod
    def create_change_op_request_message(user, message, change_op_request):
        return ChangeOPRequestMessage.objects.create(
            created_at=timezone.now(),
            creator=user,
            message=message,
            change_op_request=change_op_request,
        )

    def login_op_user(self):
        self.client.logout()
        self.client.login(username="op@opct.com", password="testpassword1")

    def login_user_user(self):
        self.client.logout()
        self.client.login(username="user@opct.com", password="testpassword1")

    def login_organization_user(self):
        self.client.logout()
        self.client.login(username="organization@opct.com", password="testpassword1")
