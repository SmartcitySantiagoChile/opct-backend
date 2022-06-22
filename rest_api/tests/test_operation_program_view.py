import json

from django.urls import reverse
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, \
    HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from rest_framework.test import APIRequestFactory

from rest_api.models import OperationProgram, OPChangeLog, OperationProgramType
from rest_api.serializers import OperationProgramSerializer
from rest_api.tests.test_views_base import BaseTestCase


class OperationProgramViewSetTest(BaseTestCase):

    def setUp(self):
        super(OperationProgramViewSetTest, self).setUp()
        self.op_program = self.create_operation_program('2022-01-01', OperationProgramType.BASE)
        self.create_operation_program('2022-03-01', OperationProgramType.MODIFIED)
        self.create_operation_program('2022-07-01', OperationProgramType.BASE)
        self.create_operation_program('2022-09-17', OperationProgramType.SPECIAL)

    # ------------------------------ helper methods ------------------------------ #
    def operation_program_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("operationprogram-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code, json_process=True)

    def operation_program_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("operationprogram-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code, json_process=True)

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
        self.login_dtpm_admin_user()
        json_response = self.operation_program_list(self.client, {})
        self.assertEqual(4, len(json_response['results']))

    def test_list_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.operation_program_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_list_without_active_session(self):
        self.client.logout()
        self.operation_program_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_retrieve_with_group_permissions(self):
        self.login_dtpm_admin_user()
        json_response = self.operation_program_retrieve(self.client, self.op_program.pk)

        factory = APIRequestFactory()
        request = factory.get('/')
        serializer_context = {'request': Request(request)}

        self.assertDictEqual(OperationProgramSerializer(self.op_program, context=serializer_context).data,
                             json_response)

    def test_retrieve_with_group_permissions_and_logs(self):
        self.login_dtpm_admin_user()
        OPChangeLog.objects.create(user=self.dtpm_admin_user, operation_program=self.op_program,
                                   created_at=timezone.now(), previous_data={}, new_data={})
        json_response = self.operation_program_retrieve(self.client, self.op_program.pk)

        factory = APIRequestFactory()
        request = factory.get('/')
        serializer_context = {'request': Request(request)}
        expected_response = json.loads(
            json.dumps(OperationProgramSerializer(self.op_program, context=serializer_context).data))

        self.assertEqual(expected_response, json_response)

    def test_retrieve_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.operation_program_retrieve(self.client, self.op_program.pk, HTTP_403_FORBIDDEN)

    def test_retrieve_without_active_session(self):
        self.client.logout()
        self.operation_program_retrieve(self.client, self.op_program.pk, HTTP_403_FORBIDDEN)

    def test_create_with_group_permissions(self):
        self.login_dtpm_admin_user()
        start_at_date = "2021-01-01"
        op_type_url = reverse("operationprogramtype-detail", kwargs=dict(pk=1))
        data = {
            "start_at": start_at_date,
            "op_type": op_type_url,
        }
        self.operation_program_create(self.client, data)
        self.assertTrue(OperationProgram.objects.filter(start_at=start_at_date).exists())

    def test_create_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.operation_program_create(self.client, {}, HTTP_403_FORBIDDEN)

    def test_create_without_active_session(self):
        self.client.logout()
        self.operation_program_create(self.client, {}, HTTP_403_FORBIDDEN)

    def test_update_with_group_permissions(self):
        self.login_dtpm_admin_user()

        new_start_at_date = "2022-01-03"
        op_type_url = reverse("operationprogramtype-detail", kwargs=dict(pk=2))
        data = {
            "start_at": new_start_at_date,
            "op_type": op_type_url,
        }
        self.operation_program_patch(self.client, self.op_program.pk, data)

        # check log
        self.assertEqual(1, OPChangeLog.objects.filter(operation_program=self.op_program).count())
        op_change_data_log = OPChangeLog.objects.first()
        self.assertJSONEqual('{"date": "2022-01-01", "op_type": "Base"}', op_change_data_log.previous_data)
        self.assertJSONEqual('{"date": "2022-01-03", "op_type": "Modificado"}', op_change_data_log.new_data)
        self.assertEqual(self.dtpm_admin_user, op_change_data_log.user)

    def test_update_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.operation_program_patch(self.client, self.op_program.pk, {}, HTTP_403_FORBIDDEN)

    def test_update_without_active_session(self):
        self.client.logout()
        self.operation_program_patch(self.client, self.op_program.pk, {}, HTTP_403_FORBIDDEN)

    def test_delete_with_permissions_and_no_op_processes_related(self):
        self.login_dtpm_admin_user()
        self.operation_program_delete(self.client, self.op_program.pk)

    def test_delete_with_permissions_and_not_found(self):
        self.login_dtpm_admin_user()
        self.operation_program_delete(self.client, 1000, HTTP_404_NOT_FOUND)

    def test_delete_with_permissions_and_op_processes_related(self):
        self.login_dtpm_admin_user()
        self.create_op_process(self.dtpm_viewer_user, self.op1_organization, self.op1_contract_type,
                               op=self.op_program)
        self.operation_program_delete(self.client, self.op_program.pk, HTTP_409_CONFLICT)

    def test_delete_with_permissions_and_op_request_related(self):
        self.login_dtpm_admin_user()
        op_proces_obj = self.create_op_process(self.dtpm_viewer_user, self.op1_organization, self.op1_contract_type,
                                               op=None)
        self.create_op_request(self.dtpm_admin_user, op_proces_obj, op=self.op_program)
        self.operation_program_delete(self.client, self.op_program.pk, HTTP_409_CONFLICT)

    def test_delete_without_permissions(self):
        self.login_dtpm_viewer_user()
        self.operation_program_delete(self.client, self.op_program.pk, HTTP_403_FORBIDDEN)

    def test_delete_without_active_session(self):
        self.client.logout()
        self.operation_program_delete(self.client, self.op_program.pk, HTTP_403_FORBIDDEN)
