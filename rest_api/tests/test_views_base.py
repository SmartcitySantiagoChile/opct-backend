import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from rest_api.models import ContractType, Organization, OperationProgram, CounterPartContact, ChangeOPProcessMessage, \
    OperationProgramType, ChangeOPProcess, ChangeOPProcessStatus, ChangeOPRequest, ChangeOPRequestStatus


class BaseTestCase(APITestCase):
    fixtures = [
        "contracttypes.json",
        "operationprogramstatuses.json",
        "operationprogramtypes.json",
        "groups.json",
        "grouppermissions.json",
        "changeoprequeststatuses.json",
        "changeopprocessstatuses.json",
    ]

    GET_REQUEST = "get"
    POST_REQUEST = "post"
    PUT_REQUEST = "put"  # update
    PATCH_REQUEST = "patch"  # partial update
    DELETE_REQUEST = "delete"

    def setUp(self):
        """
        Creates organizations with users and relations between them
        OP1 refers to operator with an old contract
        OP2 refers to operator with a new contract
        """
        self.dtpm_contract_type = ContractType.objects.get(id=ContractType.BOTH)
        self.op1_contract_type = ContractType.objects.get(id=ContractType.OLD)
        self.op2_contract_type = ContractType.objects.get(id=ContractType.NEW)

        self.dtpm_organization = self.create_organization("DTPM", self.dtpm_contract_type, None)
        self.dtpm_contact_user = self.create_user("contact@dtpm.com", "testpassword1",
                                                  organization=self.dtpm_organization)

        # organization uses old contract
        self.op1_organization = self.create_organization("OP1", self.op1_contract_type, self.dtpm_organization)
        self.op1_contact_user = self.create_user("contact@op1.com", "testpassword1",
                                                 organization=self.op1_organization)

        # organization uses new contract
        self.op2_organization = self.create_organization("OP2", self.op2_contract_type, self.dtpm_organization)
        self.op2_contact_user = self.create_user("contact@op2.com", "testpassword1",
                                                 organization=self.op2_organization)

        # operator users will be attached as counterpart of DTPM organization
        CounterPartContact.objects.create(organization=self.dtpm_organization,
                                          counter_part_user=self.op1_contact_user)
        CounterPartContact.objects.create(organization=self.dtpm_organization,
                                          counter_part_user=self.op2_contact_user)

        self.dtpm_admin_user = self.create_user("admin@dtpm.com", "testpassword1", organization=self.dtpm_organization,
                                                access_to_users=True, access_to_organizations=True, access_to_ops=True)
        self.dtpm_viewer_user = self.create_user("viewer@dtpm.com", "testpassword1",
                                                 organization=self.dtpm_organization, access_to_users=False,
                                                 access_to_organizations=False, access_to_ops=False)
        self.op1_viewer_user = self.create_user("viewer@op1.com", "testpassword1", organization=self.op1_organization,
                                                access_to_users=False, access_to_organizations=False,
                                                access_to_ops=False)
        self.op2_viewer_user = self.create_user("viewer@op2.com", "testpassword1", organization=self.op2_organization,
                                                access_to_users=False, access_to_organizations=False,
                                                access_to_ops=False)
        self.user_without_organization = self.create_user("viewer@withoutorganization.com", "testpassword1",
                                                          access_to_users=False, access_to_organizations=False,
                                                          access_to_ops=False)

        self.client = APIClient()

    def _make_request(self, client, method, url, data, status_code, json_process=False, **additional_method_params):
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
            self.assertEqual(status_code, response.status_code)

        if json_process:
            return json.loads(response.content)
        return response

    @staticmethod
    def create_user(email, password, organization=None, access_to_ops=False, access_to_organizations=False,
                    access_to_users=False, access_to_upload_route_dictionary=False, role='default role'):
        user_user_attributes = {
            "email": email,
            "password": password,
            "organization": organization,
            "access_to_ops": access_to_ops,
            "access_to_organizations": access_to_organizations,
            "access_to_users": access_to_users,
            "access_to_upload_route_dictionary": access_to_upload_route_dictionary,
            "role": role,
        }
        return get_user_model().objects.create_user(**user_user_attributes)

    @staticmethod
    def create_organization(name, contract_type, default_counterpart):
        organization_params = {
            "name": name,
            "created_at": timezone.now(),
            "contract_type": contract_type,
            "default_counterpart": default_counterpart
        }
        return Organization.objects.create(**organization_params)

    @staticmethod
    def create_operation_program(start_at, op_type=OperationProgramType.BASE):
        return OperationProgram.objects.create(start_at=start_at, op_type_id=op_type)

    @staticmethod
    def create_op_process(user, counter_part, contract_type, op=None, status_id=1, title="Change OP Process test"):
        params = {
            "created_at": timezone.now(),
            "creator": user,
            "operation_program": op,
            "status": ChangeOPProcessStatus.objects.get(id=status_id),
            "counterpart": counter_part,
            "contract_type": contract_type,
            "title": title,
            "op_release_date": "2030-01-01",
        }
        return ChangeOPProcess.objects.create(**params)

    @staticmethod
    def create_op_request(user, change_op_process, reason=ChangeOPRequest.PATH_MODIFICATION, op=None, status_id=1,
                          title="Change OP Request test", related_routes=None, related_requests=None):
        if related_routes is None:
            related_routes = []
        if related_requests is None:
            related_requests = []
        params = {
            "title": title,
            "created_at": timezone.now(),
            "creator": user,
            "operation_program": op,
            "status": ChangeOPRequestStatus.objects.get(id=status_id),
            "reason": reason,
            "change_op_process": change_op_process,
            "related_routes": related_routes,
            # "related_requests": related_requests
        }
        # TODO: arreglar la asignación de solicitudes relacionadas
        return ChangeOPRequest.objects.create(**params)

    @staticmethod
    def create_counter_part_contact(organization, user):
        return CounterPartContact.objects.create(organization=organization, counter_part_user=user)

    @staticmethod
    def create_change_op_process_message(user, message, change_op_request):
        return ChangeOPProcessMessage.objects.create(
            created_at=timezone.now(),
            creator=user,
            message=message,
            change_op_request=change_op_request,
        )

    def login_dtpm_admin_user(self):
        self.client.logout()
        self.assertTrue(self.client.login(username="admin@dtpm.com", password="testpassword1"))

    def login_dtpm_viewer_user(self):
        self.client.logout()
        self.assertTrue(self.client.login(username="viewer@dtpm.com", password="testpassword1"))

    def login_op1_viewer_user(self):
        self.client.logout()
        self.assertTrue(self.client.login(username="viewer@op1.com", password="testpassword1"))

    def login_op2_viewer_user(self):
        self.client.logout()
        self.assertTrue(self.client.login(username="viewer@op2.com", password="testpassword1"))

    def login_user_without_organization(self):
        self.client.logout()
        self.assertTrue(self.client.login(username="viewer@withoutorganization.com", password="testpassword1"))


class ChangeProcessTestCase(BaseTestCase):
    pass


class ChangeRequestTestCase(BaseTestCase):
    pass


class OperationProgramTestCase(BaseTestCase):
    pass
