from django.utils import timezone

from rest_api.models import OperationProgram, ChangeOPRequest, ChangeOPRequestStatus
from .test_views_base import BaseTestCase


class OperationProgramViewSetTest(BaseTestCase):
    def test_list_with_group_permissions(self):
        self.login_op_user()
        response = self.client.get("/api/operation-programs/")
        self.assertEqual(response.status_code, 200)

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

    def test_update_without_group_permissions(self):
        self.login_user_user()
        response = self.client.put("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.login_organization_user()
        response = self.client.put("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.put("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

    def test_delete_with_permissions_and_no_change_op_request(self):
        self.login_op_user()
        date = "2021-05-01"
        self.client.post(
            "/api/operation-programs/",
            data={"start_at": date, "op_type": "/api/operation-program-types/1/"},
        )
        op = OperationProgram.objects.get(start_at=date)
        response = self.client.delete(f"/api/operation-programs/{op.id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_with_permissions_and_not_found(self):
        self.login_op_user()
        response = self.client.delete(f"/api/operation-programs/100/")
        self.assertEqual(response.status_code, 404)

    def test_delete_with_permissions_with_change_op_request(self):
        self.login_op_user()
        date = "2021-05-01"
        self.client.post(
            "/api/operation-programs/",
            data={"start_at": date, "op_type": "/api/operation-program-types/1/"},
        )
        op = OperationProgram.objects.get(start_at=date)

        params = {
            "created_at": timezone.now(),
            "creator": self.op_user,
            "op": op,
            "status": ChangeOPRequestStatus.objects.get(id=1),
            "counterpart": self.organization_base,
            "contract_type": self.contract_type,
            "title": "Change OP Request test",
        }
        ChangeOPRequest.objects.create(**params)
        response = self.client.delete(f"/api/operation-programs/{op.id}/")
        self.assertEqual(response.status_code, 409)

    def test_delete_without_permissions(self):
        self.login_user_user()
        response = self.client.delete("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.login_organization_user()
        response = self.client.delete("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.delete("/api/operation-programs/")
        self.assertEqual(response.status_code, 403)
