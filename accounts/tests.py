from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()

class AccountsAPITests(APITestCase):
    def setUp(self):
        # создаём admin, manager, user
        self.admin = User.objects.create_user(
            username="admin", password="Admin123!@#", role=User.Roles.ADMIN, is_superuser=True, is_staff=True
        )
        self.manager = User.objects.create_user(
            username="manager", password="Manager123!@#", role=User.Roles.MANAGER
        )
        self.user = User.objects.create_user(
            username="user", password="User123!@#", role=User.Roles.USER
        )
        self.client = APIClient()

    def test_register_creates_user_with_default_role_user(self):
        payload = {
            "username": "ivan",
            "password": "Qwerty123!@#",
            "email": "ivan@example.com",
            "first_name": "Иван",
            "last_name": "Иванов",
        }
        resp = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["role"], "user")

    def test_token_and_me(self):
        # логин
        resp = self.client.post("/api/auth/token/", {"username": "user", "password": "User123!@#"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        access = resp.data["access"]
        # me
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], "user")

    def test_users_list_admin_only(self):
        # как обычный пользователь — 403
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/auth/users/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # как админ — 200
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get("/api/auth/users/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(resp.data, list))

    def test_user_cannot_change_own_role(self):
        self.client.force_authenticate(user=self.user)
        # пытаемся поменять свою роль
        resp = self.client.patch(f"/api/auth/users/{self.user.id}/", {"role": "admin"}, format="json")
        # сериализатор должен запретить
        self.assertIn(resp.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

    def test_admin_can_change_role(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(f"/api/auth/users/{self.user.id}/", {"role": "manager"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["role"], "manager")


