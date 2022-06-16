from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_400_BAD_REQUEST
)

from .test_views_base import BaseTestCase
from ..models import User


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

    def user_request_change_password(self, client, data, status_code=HTTP_200_OK):
        url = reverse("change-password")
        return self._make_request(client, self.PUT_REQUEST, url, data, status_code)

    # ------------------------------ tests ----------------------------------------

    def test_list_with_organization_permissions(self):
        self.login_dtpm_admin_user()
        self.user_request_list(self.client, {})

    def test_list_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.user_request_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_list_without_active_session(self):
        self.client.logout()
        self.user_request_list(self.client, {}, HTTP_403_FORBIDDEN)

    def test_retrieve_with_group_permissions(self):
        self.login_dtpm_admin_user()
        self.user_request_retrieve(self.client, self.dtpm_admin_user.pk)

    def test_retrieve_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.user_request_retrieve(self.client, self.dtpm_admin_user.pk, HTTP_403_FORBIDDEN)

    def test_retrieve_without_active_session(self):
        self.client.logout()
        self.user_request_retrieve(self.client, self.dtpm_admin_user.pk, HTTP_403_FORBIDDEN)

    def test_create_with_group_permissions(self):
        self.login_dtpm_admin_user()
        organization = reverse("organization-detail", kwargs=dict(pk=self.dtpm_organization.pk))
        new_user_email = 'test_create_user@opct.com'
        data = {
            "email": new_user_email,
            "password": "tcupass123",
            "organization": organization,
            "access_to_ops": False,
            "access_to_organizations": False,
            "access_to_users": True,
            "role": "prosecutor",
        }

        self.user_request_create(self.client, data)
        self.assertTrue(get_user_model().objects.filter(email=new_user_email).exists())

    def test_create_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.user_request_create(self.client, {}, HTTP_403_FORBIDDEN)

    def test_create_without_active_session(self):
        self.client.logout()
        self.user_request_create(self.client, {}, HTTP_403_FORBIDDEN)

    def test_update_with_group_permissions(self):
        self.login_dtpm_admin_user()
        organization = reverse("organization-detail", kwargs=dict(pk=self.dtpm_organization.pk))
        new_user_email = 'test_create_user@dtpm.com'
        new_user_email2 = 'test_create_user2@dtpm.com'
        user = self.create_user(new_user_email, "tcupass123", role=User.PLANNING_TECHNICIAN)
        data = {
            "email": new_user_email2,
            "password": "tcupass123",
            "organization": organization,
            "access_to_ops": True,
            "access_to_organizations": True,
            "access_to_users": True,
            "role": User.PROSECUTOR,
        }
        self.user_request_patch(self.client, user.pk, data)
        user.refresh_from_db()
        self.assertTrue(user.access_to_users)
        self.assertTrue(user.access_to_organizations)
        self.assertTrue(user.access_to_ops)
        self.assertEqual(User.PROSECUTOR, user.role)
        self.assertEqual(new_user_email2, user.email)

    def test_update_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.user_request_patch(self.client, self.dtpm_admin_user.pk, {}, HTTP_403_FORBIDDEN)

    def test_update_without_active_session(self):
        self.client.logout()
        self.user_request_patch(self.client, self.dtpm_admin_user.pk, {}, HTTP_403_FORBIDDEN)

    def test_delete_with_permissions(self):
        self.login_dtpm_admin_user()
        user = self.create_user("test_create_user@opct.com", "tcupass123")
        self.user_request_delete(self.client, user.pk)

    def test_delete_with_permissions_not_found(self):
        self.login_dtpm_admin_user()
        self.user_request_delete(self.client, -1, HTTP_404_NOT_FOUND)

    def test_delete_with_permissions_with_references(self):
        self.login_dtpm_admin_user()
        user = self.create_user("test_create_user@opct.com", "tcupass123", self.dtpm_organization)
        counter_part = self.create_counter_part_contact(self.op1_organization, user)
        self.user_request_delete(self.client, user.pk, HTTP_409_CONFLICT)

    def test_delete_without_group_permissions(self):
        self.login_dtpm_viewer_user()
        self.user_request_delete(self.client, self.dtpm_viewer_user.pk, HTTP_403_FORBIDDEN)

    def test_delete_without_active_session(self):
        self.client.logout()
        self.user_request_delete(self.client, self.dtpm_viewer_user.pk, HTTP_403_FORBIDDEN)

    def test_change_password(self):
        self.login_dtpm_viewer_user()
        data = {
            'old_password': 'testpassword1',
            'new_password1': 'tcupass321123122312',
            'new_password2': 'tcupass321123122312'
        }
        self.user_request_change_password(self.client, data, HTTP_204_NO_CONTENT)

    def test_change_password_but_old_password_is_wrong(self):
        self.login_dtpm_viewer_user()
        data = {
            'old_password': 'wrong password',
            'new_password1': 'tcupass321123122312',
            'new_password2': 'tcupass321123122312'
        }
        self.user_request_change_password(self.client, data, HTTP_400_BAD_REQUEST)

    def test_change_password_but_does_not_match(self):
        self.login_dtpm_viewer_user()
        data = {
            'old_password': 'testpassword1',
            'new_password1': '12345',
            'new_password2': '56789'
        }
        self.user_request_change_password(self.client, data, HTTP_400_BAD_REQUEST)

    def test_change_password_without_active_session(self):
        self.client.logout()
        data = {
            'old_password': 'testpassword1',
            'new_password1': 'tcupass321123122312',
            'new_password2': 'tcupass321123122312'
        }
        self.user_request_change_password(self.client, data, HTTP_403_FORBIDDEN)
