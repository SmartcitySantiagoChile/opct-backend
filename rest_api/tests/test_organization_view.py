from django.utils import timezone

from rest_api.models import Organization
from .test_views_base import BaseTestCase


class OrganizationViewSetTest(BaseTestCase):
    def test_list_with_group_permissions(self):
        self.login_organization_user()
        response = self.client.get("/api/organizations/")
        self.assertEqual(response.status_code, 200)

    def test_list_without_group_permissions(self):
        self.login_user_user()
        response = self.client.get("/api/organizations/")
        self.assertEqual(response.status_code, 403)

        self.login_op_user()
        response = self.client.get("/api/organizations/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.get("/api/organizations/")
        self.assertEqual(response.status_code, 403)

    def test_create_with_group_permissions(self):
        self.login_organization_user()

        response = self.client.post(
            "/api/organizations/",
            data={
                "name": "Organization Test",
                "created_at": timezone.now(),
                "contract_type": "/api/contract-types/1/",
                "default_counterpart": "/api/organizations/1/",
                "default_user_contact": "/api/users/1/",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_create_without_group_permissions(self):
        self.login_user_user()
        response = self.client.post("/api/organizations/")
        self.assertEqual(response.status_code, 403)

        self.login_op_user()
        response = self.client.post("/api/organizations/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.post("/api/organizations/")
        self.assertEqual(response.status_code, 403)

    def test_update_with_group_permissions(self):
        self.login_organization_user()

        self.client.post(
            "/api/organizations/",
            data={
                "name": "Organization Test 2",
                "created_at": timezone.now(),
                "contract_type": f"/api/contract-types/{self.contract_type.id}/",
                "default_counterpart": f"/api/organizations/{self.organization_base.id}/",
                "default_user_contact": f"/api/users/{self.organization_user.id}/",
            },
        )
        organization = Organization.objects.get(name="Organization Test 2")
        response = self.client.put(
            f"/api/organizations/{organization.id}/",
            data={
                "name": "Organization Test 3",
                "created_at": timezone.now(),
                "contract_type": f"/api/contract-types/{self.contract_type.id}/",
                "default_counterpart": f"/api/organizations/{self.organization_base.id}/",
                "default_user_contact": f"/api/users/{self.organization_user.id}/",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_update_without_group_permissions(self):
        self.login_user_user()
        response = self.client.put("/api/organizations/1/")
        self.assertEqual(response.status_code, 403)

        self.login_op_user()
        response = self.client.put("/api/organizations/1/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.put("/api/organizations/1/")
        self.assertEqual(response.status_code, 403)

    def test_delete_with_permissions_and_no_users(self):
        self.login_organization_user()

        response = self.client.post(
            "/api/organizations/",
            data={
                "name": "Organization Test 4",
                "created_at": timezone.now(),
                "contract_type": f"/api/contract-types/{self.contract_type.id}/",
                "default_counterpart": f"/api/organizations/{self.organization_base.id}/",
                "default_user_contact": f"/api/users/{self.organization_user.id}/",
            },
        )
        organization = Organization.objects.get(name="Organization Test 4")
        response = self.client.delete(f"/api/organizations/{organization.id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_with_permissions_and_not_found(self):
        self.login_organization_user()
        response = self.client.delete(f"/api/organizations/100/")
        self.assertEqual(response.status_code, 404)

    def test_delete_with_permissions_with_users(self):
        self.login_organization_user()

        self.client.post(
            "/api/organizations/",
            data={
                "name": "Organization Test 5",
                "created_at": timezone.now(),
                "contract_type": f"/api/contract-types/{self.contract_type.id}/",
                "default_counterpart": f"/api/organizations/{self.organization_base.id}/",
                "default_user_contact": f"/api/users/{self.organization_user.id}/",
            },
        )
        organization = Organization.objects.get(name="Organization Test 5")
        self.organization_user.organization = organization
        self.organization_user.save()
        response = self.client.delete(f"/api/organizations/{organization.id}/")
        self.assertEqual(response.status_code, 409)

    def test_delete_without_permissions(self):
        self.login_user_user()
        response = self.client.delete("/api/organizations/1/")
        self.assertEqual(response.status_code, 403)

        self.login_op_user()
        response = self.client.delete("/api/organizations/1/")
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        response = self.client.delete("/api/organizations/1/")
        self.assertEqual(response.status_code, 403)
