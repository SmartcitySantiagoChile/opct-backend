from django.urls import reverse
from django.utils import timezone
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from rest_api.models import Organization
from .test_views_base import BaseTestCase


class OrganizationViewSetTest(BaseTestCase):
    # ------------------------------ helper methods ------------------------------ #
    def organization_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("organization-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def organization_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("organization-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

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
        self.login_organization_user()
        self.organization_list(self.client, {})

    def test_retrieve_with_group_permissions(self):
        organization = self.create_organization("Test Organization", self.contract_type)
        self.login_organization_user()
        self.organization_retrieve(self.client, organization.pk)
        organization.delete()

    def test_create_with_group_permissions(self):
        self.login_organization_user()
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse(
            "organization-detail", kwargs=dict(pk=self.organization_base.pk)
        )
        data = {
            "name": "Organization Test",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.organization_create(self.client, data)
        Organization.objects.get(name="Organization Test").delete()

    def test_create_without_group_permissions(self):
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse(
            "organization-detail", kwargs=dict(pk=self.organization_base.pk)
        )
        data = {
            "name": "Organization Test",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.login_user_user()
        self.organization_create(self.client, data, HTTP_403_FORBIDDEN)

        self.login_op_user()
        self.organization_create(self.client, data, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.organization_create(self.client, data, HTTP_403_FORBIDDEN)

    def test_update_with_group_permissions(self):
        self.login_organization_user()
        organization = self.create_organization("Organization Test", self.contract_type)
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse(
            "organization-detail", kwargs=dict(pk=self.organization_base.pk)
        )
        data = {
            "name": "Organization Test 2",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.organization_patch(self.client, organization.pk, data)

    def test_update_without_group_permissions(self):
        organization = self.create_organization("Organization Test", self.contract_type)
        contract_type_url = reverse("contracttype-detail", kwargs=dict(pk=1))
        organization_url = reverse(
            "organization-detail", kwargs=dict(pk=self.organization_base.pk)
        )
        data = {
            "name": "Organization Test 2",
            "created_at": timezone.now(),
            "contract_type": contract_type_url,
            "default_counterpart": organization_url,
        }
        self.login_user_user()
        self.organization_patch(self.client, organization.pk, data, HTTP_403_FORBIDDEN)

        self.login_op_user()
        self.organization_patch(self.client, organization.pk, data, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.organization_patch(self.client, organization.pk, data, HTTP_403_FORBIDDEN)

    def test_delete_with_permissions_and_no_users(self):
        self.login_organization_user()
        organization = self.create_organization("Organization Test", self.contract_type)
        self.organization_delete(self.client, organization.pk)

    def test_delete_with_permissions_and_not_found(self):
        self.login_organization_user()
        self.organization_delete(self.client, 2, HTTP_404_NOT_FOUND)

    def test_delete_with_permissions_with_users(self):
        self.login_organization_user()
        organization = self.create_organization("Organization Test", self.contract_type)
        self.organization_user.organization = organization
        self.organization_user.save()
        self.organization_delete(self.client, organization.pk, HTTP_409_CONFLICT)
        self.organization_user.organization = None
        self.organization_user.save()
        organization.delete()

    def test_delete_without_permissions(self):
        self.login_user_user()
        organization = self.create_organization("Organization Test", self.contract_type)
        self.organization_delete(self.client, organization.pk, HTTP_403_FORBIDDEN)

        self.login_op_user()
        self.organization_delete(self.client, organization.pk, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.organization_delete(self.client, organization.pk, HTTP_403_FORBIDDEN)
        organization.delete()
