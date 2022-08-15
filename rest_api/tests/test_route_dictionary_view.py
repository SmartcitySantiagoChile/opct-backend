import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from rest_api.models import OperationProgramType, RouteDictionary
from rest_api.tests.test_views_base import BaseTestCase


class RouteDictionaryViewSetTest(BaseTestCase):

    def setUp(self):
        super(RouteDictionaryViewSetTest, self).setUp()
        self.op_program = self.create_operation_program('2022-01-01', OperationProgramType.BASE)
        self.change_op_process = self.create_op_process(self.dtpm_viewer_user, self.op1_organization,
                                                        self.op1_contract_type, op=self.op_program)
        self.change_op_request = self.create_op_request(self.dtpm_viewer_user, self.change_op_process)

    def add_permission_to_op1_viewer_user(self):
        self.op1_viewer_user.groups.add(Group.objects.get(name='Upload Route Dictionary'))

    # ------------------------------ helper methods ------------------------------ #
    def action_update_definitions(self, client, data, status_code=status.HTTP_200_OK):
        url = reverse('routedictionary-update-definitions')
        return self._make_request(client, self.POST_REQUEST, url, data, status_code, format='multipart',
                                  json_process=True)

    # ------------------------------ tests ----------------------------------------
    def test_upload_file_without_permission(self):
        self.login_op1_viewer_user()
        self.action_update_definitions(self.client, {}, status_code=status.HTTP_403_FORBIDDEN)

    def test_call_endponit_without_file(self):
        self.login_op1_viewer_user()
        self.add_permission_to_op1_viewer_user()
        data = {}
        self.action_update_definitions(self.client, data, status_code=status.HTTP_400_BAD_REQUEST)

    def test_upload_empty_file(self):
        self.login_op1_viewer_user()
        self.add_permission_to_op1_viewer_user()

        file_obj = SimpleUploadedFile('filename.csv', b'', content_type='text/csv')
        data = {
            "files": [file_obj],
        }
        self.action_update_definitions(self.client, data, status_code=status.HTTP_400_BAD_REQUEST)

    def test_upload_file(self):
        """
        create and update records in dict
        """
        self.login_op1_viewer_user()
        self.add_permission_to_op1_viewer_user()

        RouteDictionary.objects.create(ts_code='B80y', user_route_code='410', service_name='INYECCION', operator='6')

        file_path = os.path.join(settings.BASE_DIR, 'rest_api', 'tests', 'route_dictionary.csv')
        with open(file_path, 'rb') as csv_file:
            file_obj = SimpleUploadedFile('filename.csv', csv_file.read(), content_type='text/csv')
        data = {
            "files": [file_obj],
        }
        response = self.action_update_definitions(self.client, data)

        self.assertEqual(386, response['created'])
        self.assertEqual(1, response['updated'])
        self.assertEqual(387, RouteDictionary.objects.count())

    def test_upload_gz_file(self):
        """
        upload gz file
        """
        self.login_op1_viewer_user()
        self.add_permission_to_op1_viewer_user()

        file_path = os.path.join(settings.BASE_DIR, 'rest_api', 'tests', 'route_dictionary.csv.gz')
        with open(file_path, 'rb') as csv_file:
            file_obj = SimpleUploadedFile('filename.csv.gz', csv_file.read(), content_type='text/csv')
        data = {
            "files": [file_obj],
        }
        self.action_update_definitions(self.client, data)

    def test_upload_zip_file(self):
        """
        upload gz file
        """
        self.login_op1_viewer_user()
        self.add_permission_to_op1_viewer_user()

        file_path = os.path.join(settings.BASE_DIR, 'rest_api', 'tests', 'route_dictionary.zip')
        with open(file_path, 'rb') as csv_file:
            file_obj = SimpleUploadedFile('filename.zip', csv_file.read(), content_type='text/csv')
        data = {
            "files": [file_obj],
        }
        self.action_update_definitions(self.client, data)
