from django.urls import reverse
from django.utils import timezone
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from rest_api.models import OperationProgram, OPChangeDataLog
from .test_views_base import BaseTestCase


class OperationProgramViewSetTest(BaseTestCase):

    # ------------------------------ helper methods ------------------------------ #
    def operation_program_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("operationprogram-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def operation_program_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("operationprogram-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def operation_program_create(self, client, data, status_code=HTTP_201_CREATED):
        url = reverse("operationprogram-list")
        return self._make_request(client, self.POST_REQUEST, url, data, status_code)

    def operation_program_patch(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("operationprogram-detail", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def operation_program_delete(self, client, pk, status_code=HTTP_204_NO_CONTENT):
        url = reverse("operationprogram-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.DELETE_REQUEST, url, data, status_code)

    # ------------------------------ tests ---------------------------------------- #
    def test_list_with_group_permissions(self):
        self.login_op_user()
        self.operation_program_list(self.client, {})

    def test_list_without_group_permissions(self):
        self.login_user_user()
        self.operation_program_list(self.client, {}, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.operation_program_list(self.client, {}, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.operation_program_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_retrieve_with_group_permissions(self):
        op = self.create_op("2021-10-29")
        self.login_op_user()
        self.operation_program_retrieve(self.client, op.pk)
        op.delete()

    def test_retrieve_with_group_permissions_and_logs(self):
        op = self.create_op("2021-10-29")
        self.login_op_user()
        op_change_data_log = OPChangeDataLog(
            user=self.op_user,
            op=op,
            created_at=timezone.now(),
            previous_data={},
            new_data={},
        )
        op_change_data_log.save()
        self.operation_program_retrieve(self.client, op.pk)
        op_change_data_log.delete()
        op.delete()

    def test_retrieve_without_group_permissions(self):
        op = self.create_op("2021-10-29")

        self.login_user_user()
        self.operation_program_retrieve(self.client, op.pk, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.operation_program_retrieve(self.client, op.pk, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.operation_program_retrieve(self.client, op.pk, HTTP_403_FORBIDDEN)
        op.delete()

    def test_create_with_group_permissions(self):
        self.login_op_user()
        start_at_date = "2021-01-01"
        op_type_url = reverse("operationprogramtype-detail", kwargs=dict(pk=1))
        data = {
            "start_at": start_at_date,
            "op_type": op_type_url,
        }
        self.operation_program_create(self.client, data)
        OperationProgram.objects.get(start_at=start_at_date).delete()

    def test_create_without_group_permissions(self):
        start_at_date = "2021-01-01"
        op_type_url = reverse("operationprogramtype-detail", kwargs=dict(pk=1))
        data = {
            "start_at": start_at_date,
            "op_type": op_type_url,
        }

        self.login_user_user()
        self.operation_program_create(self.client, data, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.operation_program_create(self.client, data, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.operation_program_create(self.client, data, HTTP_403_FORBIDDEN)

    def test_update_with_group_permissions(self):
        self.login_op_user()
        start_at_date = "2021-01-01"
        op = self.create_op(start_at_date)

        new_start_at_date = "2021-01-02"
        op_type_url = reverse("operationprogramtype-detail", kwargs=dict(pk=1))
        data = {
            "start_at": new_start_at_date,
            "op_type": op_type_url,
        }
        self.operation_program_patch(self.client, op.pk, data)
        op.delete()

    def test_update_without_group_permissions(self):
        start_at_date = "2021-01-01"
        op = self.create_op(start_at_date)

        new_start_at_date = "2021-01-02"
        op_type_url = reverse("operationprogramtype-detail", kwargs=dict(pk=1))
        data = {
            "start_at": new_start_at_date,
            "op_type": op_type_url,
        }

        self.login_user_user()
        self.operation_program_patch(self.client, op.pk, data, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.operation_program_patch(self.client, op.pk, data, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.operation_program_patch(self.client, op.pk, data, HTTP_403_FORBIDDEN)
        op.delete()

    def test_delete_with_permissions_and_no_change_op_request(self):
        self.login_op_user()
        date = "2021-05-01"
        op = self.create_op(date)
        self.operation_program_delete(self.client, op.pk)
        op.delete()

    def test_delete_with_permissions_and_not_found(self):
        self.login_op_user()
        self.operation_program_delete(self.client, 1, HTTP_404_NOT_FOUND)

    def test_delete_with_permissions_with_change_op_request(self):
        self.login_op_user()
        date = "2021-05-01"
        op = self.create_op(date)
        change_op_request = self.create_change_op_request(
            self.op_user, op, self.organization_base, self.contract_type
        )
        self.operation_program_delete(self.client, op.pk, HTTP_409_CONFLICT)
        change_op_request.delete()
        op.delete()

    def test_delete_without_permissions(self):
        date = "2021-05-01"
        op = self.create_op(date)

        self.login_user_user()
        self.operation_program_delete(self.client, op.pk, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.operation_program_delete(self.client, op.pk, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.operation_program_delete(self.client, op.pk, HTTP_403_FORBIDDEN)
        op.delete()
