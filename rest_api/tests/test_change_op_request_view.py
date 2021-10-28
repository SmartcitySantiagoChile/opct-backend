from collections import OrderedDict

from django.utils import timezone

from rest_api.models import (
    OperationProgram,
    ChangeOPRequest,
    ChangeOPRequestStatus,
    OperationProgramType,
)
from .test_views_base import BaseTestCase
from ..serializers import ChangeOPRequestSerializer


class ChangeOPRequestViewSetTest(BaseTestCase):
    def setUp(self) -> None:
        super(ChangeOPRequestViewSetTest, self).setUp()
        self.organization_base_2 = self.create_organization(
            "ChangeOPRequest", self.contract_type, self.organization_contact_user
        )

        self.op_user_2 = self.create_op_user(
            "op2@opct.com", "testpassword1", self.organization_base_2
        )

        op = OperationProgram.objects.create(
            start_at="2021-05-01", op_type=OperationProgramType.objects.get(id=1)
        )

        params = {
            "created_at": timezone.now(),
            "creator": self.op_user_2,
            "op": op,
            "status": ChangeOPRequestStatus.objects.get(id=1),
            "counterpart": self.organization_base_2,
            "contract_type": self.contract_type,
            "title": "Change OP Request test",
        }
        self.change_op_request = ChangeOPRequest.objects.create(**params)

    def test_list_with_no_organization_permissions(self):
        self.login_op_user()
        response = self.client.get("/api/change-op-requests/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([], response.data)

    def test_list_with_organization_permissions(self):
        self.client.logout()
        self.client.login(username="op2@opct.com", password="testpassword1")
        response = self.client.get("/api/change-op-requests/")
        serializer_data = ChangeOPRequestSerializer(
            self.change_op_request, context={"request": None}
        ).data
        expected_response = [
            OrderedDict(
                [
                    ("url", f'http://testserver{serializer_data["url"]}'),
                    ("created_at", serializer_data["created_at"]),
                    ("title", serializer_data["title"]),
                    ("message", serializer_data["message"]),
                    ("updated_at", serializer_data["updated_at"]),
                    ("creator", f'http://testserver{serializer_data["creator"]}'),
                    ("op", f'http://testserver{serializer_data["op"]}'),
                    ("status", f'http://testserver{serializer_data["status"]}'),
                    (
                        "counterpart",
                        f'http://testserver{serializer_data["counterpart"]}',
                    ),
                    (
                        "contract_type",
                        f'http://testserver{serializer_data["contract_type"]}',
                    ),
                ]
            )
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_list_without_group_permissions(self):
        self.login_user_user()
        response = self.client.get("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.login_organization_user()
        response = self.client.get("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.get("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

    def test_create_with_group_permissions(self):
        self.login_op_user()

        response = self.client.post(
            "/api/operation-programs/",
            data={
                "start_at": "2021-01-01",
                "op_type": "/api/operation-program-types/1/",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_create_without_group_permissions(self):
        self.login_user_user()
        response = self.client.post("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.login_organization_user()
        response = self.client.post("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.post("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

    def test_update_with_group_permissions(self):
        self.login_op_user()
        date = "2021-01-01"
        self.client.post(
            "/api/operation-programs/",
            data={"start_at": date, "op_type": "/api/operation-program-types/1/"},
        )
        op = OperationProgram.objects.get(start_at=date)
        response = self.client.put(
            f"/api/operation-programs/{op.id}/",
            data={
                "start_at": "2021-01-02",
                "op_type": "/api/operation-program-types/1/",
            },
        )
        self.assertEqual(response.status_code, 200)
