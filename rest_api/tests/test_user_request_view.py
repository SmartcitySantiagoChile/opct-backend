from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from .test_views_base import BaseTestCase


class UserRequestViewSetTest(BaseTestCase):
    def setUp(self) -> None:
        super(UserRequestViewSetTest, self).setUp()

    # ------------------------------ helper methods ------------------------------ #
    def user_request_list(self, client, data, status_code=HTTP_200_OK):
        url = reverse("user-list")
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def user_request_retrieve(self, client, pk, status_code=HTTP_200_OK):
        url = reverse("user-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.GET_REQUEST, url, data, status_code)

    def user_request_create(self, client, data, status_code=HTTP_201_CREATED):
        url = reverse("user-list")
        return self._make_request(client, self.POST_REQUEST, url, data, status_code)

    def user_request_patch(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("user-detail", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    def user_request_delete(self, client, pk, status_code=HTTP_204_NO_CONTENT):
        url = reverse("user-detail", kwargs=dict(pk=pk))
        data = dict()
        return self._make_request(client, self.DELETE_REQUEST, url, data, status_code)

    def user_request_change_password(self, client, pk, data, status_code=HTTP_200_OK):
        url = reverse("user-change-password", kwargs=dict(pk=pk))
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    # ------------------------------ tests ----------------------------------------

    def test_list_with_organization_permissions(self):
        self.login_user_user()
        self.user_request_list(self.client, {})

    def test_list_without_group_permissions(self):
        self.login_op_user()
        self.user_request_list(self.client, {}, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.user_request_list(self.client, {}, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.user_request_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_retrieve_with_group_permissions(self):
        self.login_user_user()
        self.user_request_retrieve(self.client, self.user_user.pk)

    def test_retrieve_without_group_permissions(self):
        self.login_op_user()
        self.user_request_retrieve(self.client, self.user_user.pk, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.user_request_retrieve(self.client, self.user_user.pk, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.user_request_retrieve(self.client, self.user_user.pk, HTTP_403_FORBIDDEN)

    def test_create_with_group_permissions(self):
        self.login_user_user()
        organization = reverse(
            "organization-detail", kwargs=dict(pk=self.organization_base.pk)
        )
        data = {
            "email": "test_create_user@opct.com",
            "password": "tcupass123",
            "organization": organization,
            "access_to_ops": False,
            "access_to_organizations": False,
            "access_to_users": True,
            "role": "Técnico de planificación",
        }

        self.user_request_create(self.client, data)
        user = get_user_model().objects.get(email="test_create_user@opct.com")
        user.delete()

    def test_create_without_group_permissions(self):
        self.login_op_user()
        self.user_request_create(self.client, {}, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.user_request_create(self.client, {}, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.user_request_create(self.client, {}, HTTP_403_FORBIDDEN)

    def test_update_with_group_permissions(self):
        self.login_user_user()
        organization = reverse(
            "organization-detail", kwargs=dict(pk=self.organization_base.pk)
        )
        user = self.create_user_user("test_create_user@opct.com", "tcupass123")
        data = {
            "email": "test_create_user@opct.com",
            "password": "tcupass123",
            "organization": organization,
            "access_to_ops": False,
            "access_to_organizations": False,
            "access_to_users": True,
            "role": "Técnico de planificación",
        }
        self.user_request_patch(self.client, user.pk, data)
        user.delete()

    def test_update_without_group_permissions(self):
        self.login_op_user()
        self.user_request_patch(self.client, self.user_user.pk, {}, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.user_request_patch(self.client, self.user_user.pk, {}, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.user_request_patch(self.client, self.user_user.pk, {}, HTTP_403_FORBIDDEN)

    def test_delete_with_permissions(self):
        self.login_user_user()
        user = self.create_user_user("test_create_user@opct.com", "tcupass123")
        self.user_request_delete(self.client, user.pk)

    def test_delete_with_permissions_not_found(self):
        self.login_user_user()
        self.user_request_delete(self.client, -1, HTTP_404_NOT_FOUND)

    def test_delete_with_permissions_with_references(self):
        self.login_user_user()
        user = self.create_user_user(
            "test_create_user@opct.com", "tcupass123", self.organization_base
        )
        counter_part = self.create_counter_part_contact(
            self.organization_base, user, self.organization_base
        )
        self.user_request_delete(self.client, user.pk, HTTP_409_CONFLICT)
        counter_part.delete()
        user.delete()

    def test_delete_without_group_permissions(self):
        self.login_op_user()
        self.user_request_delete(self.client, self.user_user.pk, HTTP_403_FORBIDDEN)

        self.login_organization_user()
        self.user_request_delete(self.client, self.user_user.pk, HTTP_403_FORBIDDEN)

        self.client.logout()
        self.user_request_delete(self.client, self.user_user.pk, HTTP_403_FORBIDDEN)

    def test_change_password(self):
        self.login_user_user()
        user = self.create_user_user(
            "test_create_user@opct.com", "tcupass123", self.organization_base
        )
        data = {"password": "tcupass321"}
        self.user_request_change_password(self.client, user.pk, data)
        user.delete()

    def test_change_password_incorrect_user(self):
        self.login_user_user()
        user = self.create_user_user(
            "test_create_user@opct.com", "tcupass123", self.organization_base
        )
        data = {"password": "tcupass321"}
        self.user_request_change_password(self.client, -1, data, HTTP_404_NOT_FOUND)
        user.delete()
