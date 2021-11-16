from collections import OrderedDict

from django.test.client import RequestFactory
from django.urls import get_resolver
from django.urls import reverse
from django.utils import timezone
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from .test_views_base import BaseTestCase
from ..serializers import ChangeOPRequestSerializer


class ChangeOPRequestViewSetTest(BaseTestCase):
    def setUp(self) -> None:
        super(ChangeOPRequestViewSetTest, self).setUp()
        self.organization_base_2 = self.create_organization(
            "ChangeOPRequest", self.contract_type
        )

        self.op_user_2 = self.create_op_user(
            "op2@opct.com", "testpassword1", self.organization_base_2
        )

        self.op = self.create_op("2021-05-01")
        self.change_op_request = self.create_change_op_request(
            self.op_user_2, self.op, self.organization_base_2, self.contract_type
        )

    # ------------------------------ helper methods ------------------------------ #
    def change_op_request_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("changeoprequest-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def change_op_request_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("changeoprequest-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def change_op_request_create(self, client, data, status_code=HTTP_201_CREATED):
        url = reverse("changeoprequest-list")
        return self._make_request(client, self.POST_REQUEST, url, data, status_code)

    def change_op_request_patch(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("changeoprequest-detail", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def change_op_request_delete(self, client, pk, status_code=HTTP_204_NO_CONTENT):
        url = reverse("changeoprequest-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.DELETE_REQUEST, url, data, status_code)

    def change_op_request_change_op(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("changeoprequest-change-op", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def change_op_request_change_status(
        self, client, pk, data, status_code=HTTP_200_OK
    ):
        url = reverse("changeoprequest-change-status", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def change_op_request_filter_by_op(
        self, client, op_start_at, data, status_code=HTTP_200_OK
    ):
        url = f"{reverse('changeoprequest-list')}?op__start_at={op_start_at}"
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    # ------------------------------ tests ----------------------------------------
    def test_list_with_no_organization_permissions(self):
        self.login_op_user()
        response = self.change_op_request_list(self.client, {})
        self.assertEqual([], response.data)

    def test_list_with_organization_permissions(self):
        self.client.logout()
        self.client.login(username="op2@opct.com", password="testpassword1")
        response = self.change_op_request_list(self.client, {})
        url = reverse("changeoprequest-list")
        context = {"request": RequestFactory().get(url)}
        serializer_data = ChangeOPRequestSerializer(
            self.change_op_request, context=context
        ).data
        expected_response = [
            OrderedDict(
                [
                    ("url", serializer_data["url"]),
                    ("created_at", serializer_data["created_at"]),
                    ("title", serializer_data["title"]),
                    ("message", serializer_data["message"]),
                    ("updated_at", serializer_data["updated_at"]),
                    ("reason", serializer_data["reason"]),
                    ("op_release_date", serializer_data["op_release_date"]),
                    ("creator", serializer_data["creator"]),
                    ("op", serializer_data["op"]),
                    ("status", serializer_data["status"]),
                    (
                        "counterpart",
                        serializer_data["counterpart"],
                    ),
                    (
                        "contract_type",
                        serializer_data["contract_type"],
                    ),
                ]
            )
        ]
        self.assertEqual(response.data, expected_response)

    def test_retrieve_with_group_permissions(self):
        self.login_op_user()
        self.change_op_request_retrieve(self.client, self.change_op_request.pk)

    def test_create_with_group_permissions(self):
        self.login_op_user()
        data = {
            "created_at": timezone.now(),
            "creator": reverse("user-detail", kwargs=dict(pk=self.op_user.pk)),
            "op": reverse("operationprogram-detail", kwargs=dict(pk=self.op.pk)),
            "status": reverse("changeoprequeststatus-detail", kwargs=dict(pk=1)),
            "counterpart": reverse(
                "organization-detail", kwargs=dict(pk=self.organization_base.pk)
            ),
            "contract_type": reverse(
                "contracttype-detail", kwargs=dict(pk=self.contract_type.pk)
            ),
            "title": "Change OP Request TEST",
            "message": "test",
            "updated_at": timezone.now(),
            "op_release_date": "2030-01-01",
            "reason": "other",
        }

        self.change_op_request_create(self.client, data)

    def test_update_with_group_permissions(self):
        self.login_op_user()
        data = {
            "created_at": timezone.now(),
            "creator": reverse("user-detail", kwargs=dict(pk=self.op_user.pk)),
            "op": reverse("operationprogram-detail", kwargs=dict(pk=self.op.pk)),
            "status": reverse("changeoprequeststatus-detail", kwargs=dict(pk=1)),
            "counterpart": reverse(
                "organization-detail", kwargs=dict(pk=self.organization_base.pk)
            ),
            "contract_type": reverse(
                "contracttype-detail", kwargs=dict(pk=self.contract_type.pk)
            ),
            "title": "Change OP Request TEST",
            "message": "test",
            "updated_at": timezone.now(),
            "op_release_date": "2030-01-01",
            "reason": "other",
        }
        self.change_op_request_patch(self.client, self.change_op_request.pk, data)

    def test_delete_not_implemented(self):
        self.login_op_user()
        self.change_op_request_delete(
            self.client, self.change_op_request.pk, HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_change_op_request(self):
        self.login_op_user()
        new_op = self.create_op("2040-04-20")
        data = {"op": new_op.pk}
        self.change_op_request_change_op(self.client, self.change_op_request.pk, data)

    def test_change_op_request_with_same_op(self):
        self.login_op_user()
        data = {"op": self.op.pk}
        self.change_op_request_change_op(self.client, self.change_op_request.pk, data)

    def test_change_op_not_found_request(self):
        self.login_op_user()
        data = {"op": 5}
        self.change_op_request_change_op(
            self.client, self.change_op_request.pk, data, HTTP_404_NOT_FOUND
        )

    def test_change_status_request(self):
        self.login_op_user()
        data = {"status": 2}
        self.change_op_request_change_status(
            self.client, self.change_op_request.pk, data
        )

    def test_change_status_not_found_request(self):
        self.login_op_user()
        data = {"status": -1}
        self.change_op_request_change_status(
            self.client, self.change_op_request.pk, data, HTTP_404_NOT_FOUND
        )

    def test_change_op_request_filter_by_op(self):
        self.login_op_user()
        self.change_op_request_filter_by_op(self.client, "2021-10-25", {})
