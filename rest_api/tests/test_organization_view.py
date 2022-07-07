from django.urls import reverse
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_204_NO_CONTENT, \
    HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from rest_framework.test import APIRequestFactory

from rest_api.models import Organization
from rest_api.serializers import OrganizationSerializer
from rest_api.tests.test_views_base import BaseTestCase


class OrganizationViewSetTest(BaseTestCase):
    # ------------------------------ helper methods ------------------------------ #
    def organization_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("organization-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code, json_process=True)

    def organization_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("organization-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code, json_process=True)

    def organization_create(self, client, data, status_code=HTTP_201_CREATED):
        url = reverse("organization-list")
        return self._make_request(client, self.POST_REQUEST, url, data, status_code)

    def organization_patch(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("organization-detail", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def organization_delete(self, client, pk, status_code=HTTP_204_NO_CONTENT):
        url = reverse("organization-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.DELETE_REQUEST, url, data, status_code)

    # ------------------------------ tests ---------------------------------------- #
    def test_list_with_group_permissions(self):
        self.login_dtpm_admin_user()
        json_response = self.organization_list(self.client, {})
        self.assertEqual(3, len(json_response))

    def test_list_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.organization_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_list_without_active_session(self):
        self.client.logout()
        self.organization_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_retrieve_with_group_permissions(self):
        organization = self.create_organization("Test Organization", self.dtpm_contract_type)
        self.login_dtpm_admin_user()
        json_response = self.organization_retrieve(self.client, organization.pk)

        factory = APIRequestFactory()
        request = factory.get('/')

        serializer_context = {
            'request': Request(request),
        }

        self.assertDictEqual(OrganizationSerializer(organization, context=serializer_context).data, json_response)

    def test_retrieve_without_group_permissions(self):
        organization = self.create_organization("Test Organization", self.dtpm_contract_type)
        self.login_dtpm_viewer_user()
        self.organization_retrieve(self.client, organization.pk, HTTP_403_FORBIDDEN)

    def test_retrieve_without_active_session(self):
        self.client.logout()
        self.organization_retrieve(self.client, self.dtpm_organization.pk, HTTP_403_FORBIDDEN)

    def test_create_with_group_permissions(self):
        self.login_dtpm_admin_user()
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse(
            "organization-detail", kwargs=dict(pk=self.dtpm_organization.pk)
        )
        data = {
            "name": "Organization Test",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.organization_create(self.client, data)
        self.assertTrue(Organization.objects.filter(name="Organization Test").exists())

    def test_create_without_group_permissions(self):
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse(
            "organization-detail", kwargs=dict(pk=self.dtpm_organization.pk)
        )
        data = {
            "name": "Organization Test",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.login_dtpm_viewer_user()
        self.organization_create(self.client, data, HTTP_403_FORBIDDEN)

    def test_create_without_active_session(self):
        self.client.logout()
        self.organization_create(self.client, {}, HTTP_403_FORBIDDEN)

    def test_update_with_group_permissions(self):
        self.login_dtpm_admin_user()
        organization = self.create_organization("Organization Test", self.dtpm_contract_type)
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse(
            "organization-detail", kwargs=dict(pk=self.dtpm_organization.pk)
        )
        data = {
            "name": "Organization Test 2",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.organization_patch(self.client, organization.pk, data)

    def test_update_without_group_permissions(self):
        organization = self.create_organization("Organization Test", self.dtpm_contract_type)
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse("organization-detail", kwargs=dict(pk=self.dtpm_organization.pk))
        data = {
            "name": "Organization Test 2",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.login_dtpm_viewer_user()
        self.organization_patch(self.client, organization.pk, data, HTTP_403_FORBIDDEN)

    def test_update_without_active_session(self):
        self.client.logout()
        self.organization_patch(self.client, self.dtpm_organization.pk, {}, HTTP_403_FORBIDDEN)

    def test_delete_with_permissions_and_no_users(self):
        self.login_dtpm_admin_user()
        organization = self.create_organization("Organization Test", self.dtpm_contract_type)
        self.organization_delete(self.client, organization.pk)

    def test_delete_with_permissions_and_not_found(self):
        self.login_dtpm_admin_user()
        self.organization_delete(self.client, 1000, HTTP_404_NOT_FOUND)

    def test_delete_with_permissions_with_users(self):
        self.login_dtpm_admin_user()
        organization = self.create_organization("Organization Test", self.dtpm_contract_type)
        self.create_user('aaa@test.com', 'pass', organization)
        self.organization_delete(self.client, organization.pk, HTTP_409_CONFLICT)

    def test_delete_without_permissions(self):
        self.login_dtpm_viewer_user()
        self.organization_delete(self.client, self.dtpm_organization.pk, HTTP_403_FORBIDDEN)

    def test_delete_without_active_session(self):
        self.client.logout()
        self.organization_delete(self.client, self.dtpm_organization.pk, HTTP_403_FORBIDDEN)
