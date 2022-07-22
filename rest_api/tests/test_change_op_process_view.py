import json
from collections import OrderedDict

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import RequestFactory
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, \
    HTTP_405_METHOD_NOT_ALLOWED, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

from rest_api.models import OperationProgramType, ChangeOPProcess, ChangeOPRequest, ChangeOPProcessLog, \
    ChangeOPProcessStatus, ChangeOPProcessMessage, ChangeOPRequestLog
from rest_api.serializers import ChangeOPProcessSerializer
from rest_api.tests.test_views_base import BaseTestCase


class ChangeOPProcessViewSetTest(BaseTestCase):

    def setUp(self):
        super(ChangeOPProcessViewSetTest, self).setUp()
        self.op_program = self.create_operation_program('2022-01-01', OperationProgramType.BASE)
        self.change_op_process = self.create_op_process(self.dtpm_viewer_user, self.op1_organization,
                                                        self.op1_contract_type, op=self.op_program)
        self.change_op_request = self.create_op_request(self.dtpm_viewer_user, self.change_op_process)

    # ------------------------------ helper methods ------------------------------ #
    def change_op_process_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("changeopprocess-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def change_op_process_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("changeopprocess-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def change_op_process_create(self, client, data, status_code=HTTP_201_CREATED):
        url = reverse("changeopprocess-list")
        return self._make_request(client, self.POST_REQUEST, url, data, status_code)

    def change_op_process_patch(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("changeopprocess-detail", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def change_op_process_delete(self, client, pk, status_code=HTTP_204_NO_CONTENT):
        url = reverse("changeopprocess-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.DELETE_REQUEST, url, data, status_code)

    def change_op_process_change_op(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("changeopprocess-change-op", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def change_op_process_change_status(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("changeopprocess-change-status", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def change_op_process_filter_by_op(self, client, op_start_at, data, status_code=HTTP_200_OK):
        url = f"{reverse('changeopprocess-list')}?search={op_start_at}"
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def change_op_process_add_message(self, client, pk, data, status_code=HTTP_201_CREATED):
        url = reverse("changeopprocess-add-message", kwargs=dict(pk=pk))
        return self._make_request(client, self.POST_REQUEST, url, data, status_code, format='multipart')

    def change_op_process_create_change_op_request(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("changeopprocess-create-change-op-request", kwargs=dict(pk=pk))
        return self._make_request(client, self.POST_REQUEST, url, data, status_code)

    def change_op_process_update_change_op_request(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("changeopprocess-update-change-op-requests", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    # ------------------------------ tests ----------------------------------------
    def test_list_with_user_related_to_owner_organization(self):
        self.login_dtpm_viewer_user()
        response = self.change_op_process_list(self.client, {})

        url = reverse("changeoprequest-list")
        context = {"request": RequestFactory().get(url)}
        # simulate annotation
        self.change_op_process.change_op_requests_count = 1
        serializer_data = ChangeOPProcessSerializer(self.change_op_process, context=context).data
        expected_response = OrderedDict(
            [
                ("count", 1),
                ("next", None),
                ("previous", None),
                ("results", [
                    OrderedDict([
                        ("id", serializer_data["id"]),
                        ("url", serializer_data["url"]),
                        ("title", serializer_data["title"]),
                        ("created_at", serializer_data["created_at"]),
                        ("updated_at", serializer_data["updated_at"]),
                        ("counterpart", serializer_data["counterpart"],),
                        ("contract_type", serializer_data["contract_type"],),
                        ("creator", serializer_data["creator"]),
                        ("status", serializer_data["status"]),
                        ("op_release_date", serializer_data["op_release_date"]),
                        ("change_op_requests_count", serializer_data["change_op_requests_count"]),
                        ("operation_program", serializer_data["operation_program"]),
                    ])
                ]),
            ]
        )
        self.assertJSONEqual(json.dumps(response.data), json.dumps(expected_response))

    def test_list_with_user_related_to_counterpart_organization(self):
        self.login_op1_viewer_user()
        response = self.change_op_process_list(self.client, {})
        self.assertEqual(1, len(response.data['results']))

    def test_list_with_user_not_related_to_any_organization(self):
        self.login_op2_viewer_user()
        response = self.change_op_process_list(self.client, {})
        self.assertEqual(0, len(response.data['results']))

    def test_list_with_user_without_organization(self):
        self.login_user_without_organization()
        response = self.change_op_process_list(self.client, {})
        self.assertEqual(0, len(response.data['results']))

    def test_list_without_active_session(self):
        self.client.logout()
        self.change_op_process_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_retrieve_user_related_to_creator_organization(self):
        self.login_dtpm_viewer_user()
        self.change_op_process_retrieve(self.client, self.change_op_process.pk)

    def test_retrieve_user_related_to_counterpart_organization(self):
        self.login_op1_viewer_user()
        self.change_op_process_retrieve(self.client, self.change_op_process.pk)

    def test_retrieve_user_related_to_third_organization(self):
        self.login_op2_viewer_user()
        self.change_op_process_retrieve(self.client, self.change_op_process.pk, HTTP_404_NOT_FOUND)

    def test_retrieve_user_without_organization(self):
        self.login_user_without_organization()
        self.change_op_process_retrieve(self.client, self.change_op_process.pk, HTTP_404_NOT_FOUND)

    def test_retrieve_without_active_session(self):
        self.client.logout()
        self.change_op_process_retrieve(self.client, self.change_op_process.pk, HTTP_403_FORBIDDEN)

    def test_create_with_contract_type_both(self):
        self.login_dtpm_viewer_user()
        title = 'Change OP Request TEST'
        data = {
            "title": title,
            "counterpart": reverse("organization-detail", kwargs=dict(pk=self.op1_organization.pk)),
            "operation_program": reverse("operationprogram-detail", kwargs=dict(pk=self.op_program.pk)),
            "change_op_requests": []
        }

        self.change_op_process_create(self.client, data)

        change_op_process_obj = ChangeOPProcess.objects.order_by('-created_at').first()
        self.assertEqual(self.op1_contract_type.pk, change_op_process_obj.contract_type_id)
        self.assertEqual(title, change_op_process_obj.title)
        self.assertIsNotNone(change_op_process_obj.created_at)
        self.assertIsNotNone(change_op_process_obj.updated_at)
        self.assertEqual(self.op1_organization.pk, change_op_process_obj.counterpart.pk)
        self.assertEqual(self.op_program.pk, change_op_process_obj.operation_program.pk)
        self.assertEqual(self.dtpm_viewer_user, change_op_process_obj.creator)
        self.assertEqual(1, change_op_process_obj.status.pk)
        self.assertEqual(str(self.op_program.start_at), str(change_op_process_obj.op_release_date))

    def test_create_with_empty_op(self):
        self.login_dtpm_viewer_user()
        title = 'Another title'
        data = {
            "title": title,
            "counterpart": reverse("organization-detail", kwargs=dict(pk=self.op1_organization.pk)),
            "change_op_requests": []
        }

        self.change_op_process_create(self.client, data)

        change_op_process_obj = ChangeOPProcess.objects.order_by('-created_at').first()
        self.assertIsNone(change_op_process_obj.operation_program)
        self.assertIsNone(change_op_process_obj.op_release_date)

    def test_create_but_user_can_not_select_organization(self):
        self.login_op1_viewer_user()
        title = 'Another title again'
        data = {
            "title": title,
            "counterpart": reverse("organization-detail", kwargs=dict(pk=self.op2_organization.pk)),
            "change_op_requests": []
        }

        self.change_op_process_create(self.client, data, status_code=HTTP_400_BAD_REQUEST)

    def test_create_with_contract_type_old(self):
        self.login_op1_viewer_user()
        title = 'Another title again'
        data = {
            "title": title,
            "counterpart": reverse("organization-detail", kwargs=dict(pk=self.dtpm_organization.pk)),
            "change_op_requests": []
        }

        self.change_op_process_create(self.client, data)

        change_op_process_obj = ChangeOPProcess.objects.order_by('-created_at').first()
        self.assertEqual(self.op1_contract_type, change_op_process_obj.contract_type)

    def test_create_without_counterpart(self):
        self.login_op1_viewer_user()
        title = 'Another title again!'
        data = {
            "title": title,
            "change_op_requests": []
        }

        self.change_op_process_create(self.client, data, HTTP_400_BAD_REQUEST)

    def test_create_with_op_requests(self):
        self.login_dtpm_viewer_user()
        title = 'Another title'
        data = {
            "title": title,
            "counterpart": reverse("organization-detail", kwargs=dict(pk=self.op1_organization.pk)),
            "change_op_requests": [
                {
                    "title": "request title 1",
                    "reason": ChangeOPRequest.REASON_CHOICES[0][0],
                    "related_requests": [],
                    "related_routes": []
                },
                {
                    "title": "request title 2",
                    "reason": ChangeOPRequest.REASON_CHOICES[1][0],
                    "related_requests": [],
                    "related_routes": []
                },
                {
                    "title": "request title 3",
                    "reason": ChangeOPRequest.REASON_CHOICES[2][0],
                    "related_requests": [],
                    "related_routes": ['T506 00I', 'T507 00R']
                },
                {
                    "title": "request title 4",
                    "reason": ChangeOPRequest.REASON_CHOICES[3][0],
                    "related_requests": [],
                    "related_routes": []
                }
            ]
        }
        self.change_op_process_create(self.client, data)

        change_op_process_obj = ChangeOPProcess.objects.prefetch_related('change_op_requests'). \
            order_by('-created_at').first()
        self.assertEqual(4, len(change_op_process_obj.change_op_requests.all()))

        change_op_request_obj = ChangeOPRequest.objects.get(title='request title 3')
        self.assertListEqual(['T506 00I', 'T507 00R'], change_op_request_obj.related_routes)

    def test_create_with_related_op_requests(self):
        self.login_dtpm_viewer_user()

        change_op_request_pk = ChangeOPRequest.objects.first().pk
        data = {
            "title": 'change op process title',
            "counterpart": reverse("organization-detail", kwargs=dict(pk=self.op1_organization.pk)),
            "change_op_requests": [
                {
                    "title": "request title 1",
                    "reason": ChangeOPRequest.REASON_CHOICES[0][0],
                    "related_requests": [change_op_request_pk],
                    "related_routes": []
                }
            ]
        }
        self.change_op_process_create(self.client, data)
        change_op_process_obj = ChangeOPProcess.objects.prefetch_related('change_op_requests'). \
            order_by('-created_at').first()
        self.assertEqual(1, change_op_process_obj.change_op_requests.all().count())
        self.assertEqual(1, change_op_process_obj.change_op_requests.all()[0].related_requests.all().count())
        self.assertEqual(change_op_process_obj.change_op_requests.all()[0].related_requests.all()[0].pk,
                         change_op_request_pk)

    def test_add_message_without_related_requests(self):
        self.login_op1_viewer_user()
        data = {
            "message": "test message",
            "files": [],
            "related_requests": []
        }
        self.change_op_process_add_message(self.client, self.change_op_process.pk, data,
                                           status_code=HTTP_400_BAD_REQUEST)
        self.assertEqual(0, ChangeOPProcessMessage.objects.filter(change_op_process=self.change_op_process).count())

    def test_add_message_but_related_request_is_not_valid(self):
        self.login_op1_viewer_user()
        data = {
            "message": "test message",
            "files": [],
            "related_requests": json.dumps([100])
        }
        self.change_op_process_add_message(self.client, self.change_op_process.pk, data,
                                           status_code=HTTP_400_BAD_REQUEST)
        self.assertEqual(0, ChangeOPProcessMessage.objects.filter(change_op_process=self.change_op_process).count())

    def test_add_message_with_files(self):
        self.login_op1_viewer_user()
        file_obj1 = SimpleUploadedFile('filename.xlsx', b'text content',
                                       content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        file_obj2 = SimpleUploadedFile('filename.xlsx', b'text content',
                                       content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        file_obj3 = SimpleUploadedFile('filename.docx', b'another text content',
                                       content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        message_obj = 'yes, another custom message'
        data = {
            "message": message_obj,
            "files": [file_obj1, file_obj2, file_obj3],
            "related_requests": json.dumps([self.change_op_request.id])
        }
        self.change_op_process_add_message(self.client, self.change_op_process.pk, data)

        change_op_process_obj = ChangeOPProcess.objects.prefetch_related(
            'change_op_process_messages__change_op_process_message_files').order_by('-created_at').first()
        message_objs = change_op_process_obj.change_op_process_messages.all()
        for message_obj in message_objs:
            files = message_obj.change_op_process_message_files.all()
            self.assertEqual(3, len(files))
            for file_obj in files:
                self.assertIn(file_obj.filename, ['filename.xlsx', 'filename.docx'])
                file_obj.file.delete()
            self.assertEqual(1, message_obj.related_requests.count())

    def test_add_message_without_files(self):
        self.login_op1_viewer_user()
        message = 'yes, another custom message'
        data = {
            "message": message,
            "files": [],
            "related_requests": json.dumps([self.change_op_request.id])
        }
        self.change_op_process_add_message(self.client, self.change_op_process.pk, data)

        change_op_process_obj = ChangeOPProcess.objects.prefetch_related(
            'change_op_process_messages__change_op_process_message_files').order_by('-created_at').first()
        messages = change_op_process_obj.change_op_process_messages.all()
        for message in messages:
            files = message.change_op_process_message_files.all()
            self.assertEqual(0, len(files))

    def test_add_message_without_content(self):
        self.login_op1_viewer_user()
        data = {
            "message": "",
            "files": [],
            "related_requests": json.dumps([self.change_op_request.id])
        }
        self.change_op_process_add_message(self.client, self.change_op_process.pk, data,
                                           status_code=HTTP_400_BAD_REQUEST)
        self.assertEqual(0, ChangeOPProcessMessage.objects.filter(change_op_process=self.change_op_process).count())

    def test_update(self):
        self.login_op1_viewer_user()
        self.change_op_process_patch(self.client, self.change_op_process.pk, {}, HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.login_dtpm_viewer_user()
        self.change_op_process_delete(self.client, self.change_op_process.pk, HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_change_op_requests(self):
        pass

    def test_update_operation_program(self):
        self.login_dtpm_viewer_user()
        new_operation_program = self.create_operation_program("2040-04-20", OperationProgramType.MODIFIED)
        data = {"operation_program": new_operation_program.pk}
        self.change_op_process_change_op(self.client, self.change_op_process.pk, data)

        self.change_op_process.refresh_from_db()
        self.assertEqual(new_operation_program, self.change_op_process.operation_program)
        self.assertEqual(1, ChangeOPProcessLog.objects.count())
        log_obj = ChangeOPProcessLog.objects.first()
        self.assertEqual(self.dtpm_viewer_user, log_obj.user)
        self.assertEqual(self.change_op_process, log_obj.change_op_process)
        self.assertEqual(ChangeOPProcessLog.OP_CHANGE, log_obj.type)
        self.assertDictEqual(dict(date='2022-01-01', type='Base'), log_obj.previous_data)
        self.assertDictEqual(dict(date='2040-04-20', type='Modificado', update_deadlines=False), log_obj.new_data)

    def test_update_operation_program_with_deadlines(self):
        self.login_dtpm_viewer_user()
        new_operation_program = self.create_operation_program("2024-01-15")
        data = {"operation_program": new_operation_program.pk, "update_deadlines": True}
        self.change_op_process_change_op(self.client, self.change_op_process.pk, data)

        log_obj = ChangeOPProcessLog.objects.first()
        self.assertDictEqual(dict(date='2024-01-15', type='Base', update_deadlines=True), log_obj.new_data)

    def test_update_operation_program_with_same_operation_program(self):
        self.login_dtpm_viewer_user()
        data = {"operation_program": self.op_program.pk}
        self.change_op_process_change_op(self.client, self.change_op_process.pk, data)

        self.change_op_process.refresh_from_db()
        self.assertEqual(self.op_program, self.change_op_process.operation_program)
        self.assertEqual(0, ChangeOPProcessLog.objects.count())

    def test_update_operation_program_with_none(self):
        self.login_dtpm_viewer_user()
        data = {}
        self.change_op_process_change_op(self.client, self.change_op_process.pk, data)

        self.change_op_process.refresh_from_db()
        self.assertIsNone(self.change_op_process.operation_program)
        self.assertIsNone(self.change_op_process.op_release_date)
        self.assertEqual(1, ChangeOPProcessLog.objects.count())

    def test_update_operation_program_without_previos_operation_program(self):
        self.change_op_process.operation_program = None
        self.change_op_process.save()

        self.login_dtpm_viewer_user()
        data = {"operation_program": self.op_program.pk}
        self.change_op_process_change_op(self.client, self.change_op_process.pk, data)
        self.assertEqual(1, ChangeOPProcessLog.objects.count())

    def test_update_operation_program_but_it_does_not_exist(self):
        self.login_dtpm_viewer_user()
        data = {"operation_program": 5}
        self.change_op_process_change_op(self.client, self.change_op_process.pk, data, HTTP_404_NOT_FOUND)
        self.assertEqual(0, ChangeOPProcessLog.objects.count())

    def test_change_status(self):
        self.login_op1_viewer_user()
        previous_status_name = self.change_op_process.status.name
        new_status_obj = ChangeOPProcessStatus.objects.get(pk=2)
        data = {"status": new_status_obj.pk}
        self.change_op_process_change_status(self.client, self.change_op_process.pk, data)

        self.change_op_process.refresh_from_db()
        self.assertEqual(new_status_obj, self.change_op_process.status)
        self.assertEqual(1, ChangeOPProcessLog.objects.count())
        log_obj = ChangeOPProcessLog.objects.first()
        self.assertEqual(self.op1_viewer_user, log_obj.user)
        self.assertEqual(self.change_op_process, log_obj.change_op_process)
        self.assertEqual(ChangeOPProcessLog.STATUS_CHANGE, log_obj.type)
        self.assertDictEqual(dict(value=previous_status_name), log_obj.previous_data)
        self.assertDictEqual(dict(value=new_status_obj.name), log_obj.new_data)

    def test_change_status_not_found_request(self):
        self.login_dtpm_viewer_user()
        data = {"status": -1}
        self.change_op_process_change_status(self.client, self.change_op_process.pk, data, HTTP_404_NOT_FOUND)
        self.assertEqual(0, ChangeOPProcessLog.objects.count())

    def test_create_change_op_request(self):
        self.login_dtpm_viewer_user()
        related_routes = ['T506 00I', 'T507 00R']
        title = 'new title'
        reason = ChangeOPRequest.REASON_CHOICES[0][0]

        status_url = 'http://localhost:8000/api/change-op-request-statuses/12/'
        operation_program_url = 'http://localhost:8000/api/operation-programs/{}/'.format(self.op_program.pk)
        data = {
            "change_op_request": {
                "id": None,
                "title": title,
                "reason": reason,
                "related_requests": [],
                "related_routes": related_routes,
                "status": status_url,
                "operation_program": operation_program_url
            }
        }
        self.change_op_process_create_change_op_request(self.client, self.change_op_process.pk, data)

        self.assertEqual(2, ChangeOPRequest.objects.count())
        change_op_request_obj = ChangeOPRequest.objects.order_by('-id').first()
        self.assertEqual(title, change_op_request_obj.title)
        self.assertEqual(reason, change_op_request_obj.reason)
        self.assertListEqual([], list(change_op_request_obj.related_requests.all()))
        self.assertListEqual(related_routes, change_op_request_obj.related_routes)

        self.assertEqual(1, ChangeOPRequestLog.objects.count())
        log_obj = ChangeOPRequestLog.objects.first()
        self.assertEqual(self.dtpm_viewer_user, log_obj.user)
        new_change_op_request = ChangeOPRequest.objects.exclude(id=self.change_op_request.pk).first()
        self.assertEqual(new_change_op_request, log_obj.change_op_request)
        self.assertEqual(ChangeOPRequestLog.CHANGE_OP_REQUEST_CREATION, log_obj.type)
        self.assertDictEqual(dict(), log_obj.previous_data)
        expected_new_data = dict(title=title, reason="Acortamiento",
                                 operation_program=dict(date='01-01-2022', type="Base"),
                                 related_routes=", ".join(['T506 00I', 'T507 00R']), status='Solicitud observada')
        self.assertDictEqual(expected_new_data, log_obj.new_data)

    def test_update_change_op_request_with_new_data(self):
        self.login_dtpm_viewer_user()
        title = 'new title'
        related_routes = ['T506 00I', 'T507 00R']
        operation_program_url = 'http://localhost:8000/api/operation-programs/{}/'.format(self.op_program.pk)
        reason = ChangeOPRequest.REASON_CHOICES[0][0]
        status_url = 'http://localhost:8000/api/change-op-request-statuses/12/'

        # change that al values are different
        self.assertNotEqual(title, self.change_op_request.title)
        self.assertListEqual([], self.change_op_request.related_routes)
        self.assertNotEqual(self.op_program.pk, self.change_op_request.operation_program_id)
        self.assertNotEqual(reason, self.change_op_request.reason)
        self.assertNotEqual(12, self.change_op_request.status_id)

        data = {
            "change_op_requests": [{
                "id": self.change_op_request.id,
                "title": title,
                "reason": reason,
                "related_requests": [],
                "related_routes": related_routes,
                "status": status_url,
                "operation_program": operation_program_url
            }]
        }
        self.change_op_process_update_change_op_request(self.client, self.change_op_process.pk, data)

        self.assertEqual(1, ChangeOPRequest.objects.count())
        self.change_op_request.refresh_from_db()
        self.assertEqual(title, self.change_op_request.title)
        self.assertEqual(reason, self.change_op_request.reason)
        self.assertListEqual([], list(self.change_op_request.related_requests.all()))
        self.assertListEqual(related_routes, self.change_op_request.related_routes)
        self.assertEqual(self.op_program.pk, self.change_op_request.operation_program_id)
        self.assertEqual(12, self.change_op_request.status_id)

        self.assertEqual(1, ChangeOPRequestLog.objects.count())
        log_obj = ChangeOPRequestLog.objects.first()
        self.assertEqual(self.dtpm_viewer_user, log_obj.user)
        self.assertEqual(self.change_op_request, log_obj.change_op_request)
        self.assertEqual(ChangeOPRequestLog.CHANGE_OP_REQUEST_UPDATE, log_obj.type)
        expected_previous_data = dict(
            operation_program=dict(date='', type=''),
            reason='Modificación de Trazado', related_routes='', status='Evaluando admisibilidad',
            title='Change OP Request test')
        self.assertDictEqual(expected_previous_data, log_obj.previous_data)
        expected_new_data = dict(title=title, reason="Acortamiento",
                                 operation_program=dict(date='01-01-2022', type="Base"),
                                 related_routes=", ".join(['T506 00I', 'T507 00R']), status='Solicitud observada')
        self.assertDictEqual(expected_new_data, log_obj.new_data)

    def test_update_change_op_request_without_new_data(self):
        self.login_dtpm_viewer_user()

        status_url = 'http://localhost:8000/api/change-op-request-statuses/{}/'.format(self.change_op_request.status_id)
        data = {
            "change_op_requests": [{
                "id": self.change_op_request.id,
                "title": self.change_op_request.title,
                "reason": self.change_op_request.reason,
                "related_routes": self.change_op_request.related_routes,
                "status": status_url,
                "operation_program": self.change_op_request.operation_program
            }]
        }
        self.change_op_process_update_change_op_request(self.client, self.change_op_process.pk, data)

        self.assertEqual(1, ChangeOPRequest.objects.count())
        self.assertEqual(0, ChangeOPProcessLog.objects.count())
