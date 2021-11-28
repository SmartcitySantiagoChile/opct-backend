from django.urls import reverse
from django.utils import timezone
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from django.contrib.auth import get_user_model

from .test_views_base import BaseTestCase
from ..models import ChangeOPRequestMessage


class ChangeOPRequestMessageViewSetTest(BaseTestCase):
    def setUp(self) -> None:
        super(ChangeOPRequestMessageViewSetTest, self).setUp()
        self.op = self.create_op("2021-05-01")
        self.change_op_request = self.create_change_op_request(
            self.op_user, self.op, self.organization_base, self.contract_type
        )
        self.change_op_request_message = self.create_change_op_request_message(
            self.op_user, "Mensaje de ejemplo", self.change_op_request
        )

    # ------------------------------ helper methods ------------------------------ #
    def change_op_request_message_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("changeoprequestmessage-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def change_op_request_message_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("changeoprequestmessage-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def change_op_request_message_create(
        self, client, data, status_code=HTTP_201_CREATED
    ):
        url = reverse("changeoprequestmessage-list")
        return self._make_request(client, self.POST_REQUEST, url, data, status_code)

    def change_op_request_message_patch(
        self, client, pk, data, status_code=HTTP_200_OK
    ):
        url = reverse("changeoprequestmessage-detail", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def change_op_request_message_delete(
        self, client, pk, status_code=HTTP_204_NO_CONTENT
    ):
        url = reverse("changeoprequest-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.DELETE_REQUEST, url, data, status_code)

    # ------------------------------ tests ----------------------------------------
    def test_list_with_permissions(self):
        self.login_op_user()
        self.change_op_request_message_list(self.client, {})

    def test_retrieve_with_permissions(self):
        self.login_op_user()
        self.change_op_request_message_retrieve(
            self.client, self.change_op_request_message.pk
        )

    def test_create_with_permissions(self):
        self.login_op_user()
        data = {
            "created_at": timezone.now(),
            "creator": reverse("user-detail", kwargs=dict(pk=self.op_user.pk)),
            "change_op_request": reverse(
                "changeoprequest-detail", kwargs=dict(pk=self.change_op_request.pk)
            ),
            "message": "test",
        }

        self.change_op_request_message_create(self.client, data)
        ChangeOPRequestMessage.objects.get(message="test").delete()

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

    def tearDown(self) -> None:
        self.change_op_request_message.delete()
        self.change_op_request.delete()
        self.op.delete()
