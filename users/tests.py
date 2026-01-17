from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


User = get_user_model()


class UserModelTestCase(TestCase):
    """Тесты модели пользователя"""

    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "phone_number": "+79991234567",
            "city": "Москва",
        }

    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(email="user@example.com", password="testpass")
        self.assertEqual(str(user), "user@example.com")

    def test_user_without_email(self):
        """Тест: пользователь без email не создается"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass")


class UserAPITestCase(APITestCase):
    """Тесты API пользователей"""

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "phone_number": "+79991234567",
            "city": "Москва",
        }
        self.user = User.objects.create_user(**self.user_data)

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="otherpassword123",
            phone_number="+79998765432",
            city="Санкт-Петербург",
        )

    def test_register_user_success(self):
        """POST /api/users/ - успешная регистрация пользователя"""
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "phone_number": "+79991112233",
            "city": "Казань",
        }

        user_count_before = User.objects.count()

        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), user_count_before + 1)

        self.assertEqual(response.data["email"], "newuser@example.com")
        self.assertIsNotNone(response.data["id"])
        self.assertIn("phone_number", response.data)
        self.assertIn("city", response.data)

        self.assertNotIn("password", response.data)

    def test_register_user_invalid_email(self):
        """POST /api/users/ - регистрация с невалидным email"""
        data = {
            "email": "invalid-email",
            "password": "testpass123",
        }

        response = self.client.post("/api/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_email(self):
        """POST /api/users/ - регистрация с существующим email"""
        data = {
            "email": "testuser@example.com",
            "password": "anotherpassword123",
        }

        response = self.client.post("/api/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """POST /api/token/ - успешная аутентификация"""
        data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }

        response = self.client.post("/api/token/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_login_wrong_password(self):
        """POST /api/token/ - неверный пароль"""
        data = {
            "email": "testuser@example.com",
            "password": "wrongpassword",
        }

        response = self.client.post("/api/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0], "Неверный email или пароль"
        )

    def test_login_nonexistent_user(self):
        """POST /api/token/ - несуществующий пользователь"""
        data = {
            "email": "nonexistent@example.com",
            "password": "somepassword",
        }

        response = self.client.post("/api/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(
            response.data["non_field_errors"][0], "Неверный email или пароль"
        )

    def test_get_own_profile_authenticated(self):
        """GET /api/users/{id}/ - получение своего профиля"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/users/{self.user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "testuser@example.com")
        self.assertEqual(response.data["phone_number"], "+79991234567")
        self.assertEqual(response.data["city"], "Москва")

    def test_get_own_profile_unauthenticated(self):
        """GET /api/users/{id}/ - без авторизации"""
        response = self.client.get(f"/api/users/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_other_user_profile(self):
        """GET /api/users/{id}/ - попытка получить чужой профиль"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/users/{self.other_user.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_list_authenticated(self):
        """GET /api/users/ - получение списка пользователей (только себя)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "testuser@example.com")

    def test_update_own_profile(self):
        """PATCH /api/users/{id}/ - обновление своего профиля"""
        self.client.force_authenticate(user=self.user)

        update_data = {
            "phone_number": "+79998887766",
            "city": "Новосибирск",
        }

        response = self.client.patch(
            f"/api/users/{self.user.id}/", update_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "+79998887766")
        self.assertEqual(self.user.city, "Новосибирск")

    def test_update_other_user_profile(self):
        """PATCH /api/users/{id}/ - попытка обновить чужой профиль"""
        self.client.force_authenticate(user=self.user)

        update_data = {
            "city": "Взломанный город",
        }

        response = self.client.patch(
            f"/api/users/{self.other_user.id}/", update_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.city, "Санкт-Петербург")

    def test_delete_own_profile(self):
        """DELETE /api/users/{id}/ - удаление своего профиля"""
        self.client.force_authenticate(user=self.user)

        user_id = self.user.id
        response = self.client.delete(f"/api/users/{user_id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_other_user_profile(self):
        """DELETE /api/users/{id}/ - попытка удалить чужой профиль"""
        self.client.force_authenticate(user=self.user)

        other_user_id = self.other_user.id
        response = self.client.delete(f"/api/users/{other_user_id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(User.objects.filter(id=other_user_id).exists())

    def test_superuser_sees_all_users(self):
        """GET /api/users/ - суперпользователь видит всех пользователей"""

        superuser = User.objects.create_superuser(
            email="super@example.com", password="superpass123"
        )
        self.client.force_authenticate(user=superuser)

        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_superuser_updates_other_user(self):
        """PATCH /api/users/{id}/ - суперпользователь обновляет другого пользователя"""

        superuser = User.objects.create_superuser(
            email="super@example.com", password="superpass123"
        )
        self.client.force_authenticate(user=superuser)

        update_data = {
            "city": "Обновленный суперпользователем",
        }

        response = self.client.patch(
            f"/api/users/{self.user.id}/", update_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.city, "Обновленный суперпользователем")

    def test_token_refresh(self):
        """POST /api/token/refresh/ - обновление токена"""

        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        login_response = self.client.post("/api/token/", login_data, format="json")
        refresh_token = login_response.data["refresh"]

        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(
            "/api/token/refresh/", refresh_data, format="json"
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_token_verify(self):
        """POST /api/token/verify/ - проверка токена"""

        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        login_response = self.client.post("/api/token/", login_data, format="json")
        access_token = login_response.data["access"]

        verify_data = {"token": access_token}
        verify_response = self.client.post(
            "/api/token/verify/", verify_data, format="json"
        )

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
