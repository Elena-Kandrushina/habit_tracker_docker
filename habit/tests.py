from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import time

from habit.models import Habit
from habit.validators import validate_duration, validate_periodicity

User = get_user_model()


class HabitModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="test123"
        )

    def test_create_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(8, 0),
            action="Тестовая привычка",
            duration=120,
        )
        self.assertEqual(habit.action, "Тестовая привычка")


class HabitValidatorTestCase(TestCase):
    def test_validate_duration(self):
        self.assertEqual(validate_duration(120), 120)

    def test_validate_periodicity(self):
        self.assertEqual(validate_periodicity(7), 7)


class HabitAPITestCase(APITestCase):
    """Тесты API с прямыми URL-адресами"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", password="password123"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="password123"
        )

        self.habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=time(8, 0),
            action="Моя привычка",
            duration=120,
            is_public=False,
        )

        self.public_habit = Habit.objects.create(
            user=self.other_user,
            place="Парк",
            time=time(18, 0),
            action="Публичная привычка",
            duration=300,
            is_public=True,
        )

    def test_get_habits_authenticated(self):
        """GET /api/habits/ - получение своих привычек"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_habits_unauthenticated(self):
        """GET /api/habits/ - без авторизации"""
        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_habit(self):
        """POST /api/habits/ - создание привычки"""
        self.client.force_authenticate(user=self.user)
        data = {
            "place": "Офис",
            "time": "12:00:00",
            "action": "Новая привычка",
            "duration": 60,
        }
        response = self.client.post("/api/habits/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)

    def test_create_habit_invalid_duration(self):
        """POST /api/habits/ - создание с неверной длительностью"""
        self.client.force_authenticate(user=self.user)
        data = {
            "place": "Офис",
            "time": "12:00:00",
            "action": "Новая привычка",
            "duration": 121,
        }
        response = self.client.post("/api/habits/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_single_habit(self):
        """GET /api/habits/{id}/ - получение своей привычки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "Моя привычка")

    def test_get_others_private_habit(self):
        """GET /api/habits/{id}/ - попытка получить чужую приватную привычку"""
        self.client.force_authenticate(user=self.user)
        private_habit = Habit.objects.create(
            user=self.other_user,
            place="Секрет",
            time=time(23, 0),
            action="Приватная привычка",
            duration=60,
            is_public=False,
        )
        response = self.client.get(f"/api/habits/{private_habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_others_public_habit(self):
        """GET /api/habits/{id}/ - попытка получить чужую публичную привычку"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/habits/{self.public_habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_habit(self):
        """PATCH /api/habits/{id}/ - обновление своей привычки"""
        self.client.force_authenticate(user=self.user)
        data = {"place": "Обновленное место"}
        response = self.client.patch(
            f"/api/habits/{self.habit.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.place, "Обновленное место")

    def test_update_others_habit(self):
        """PATCH /api/habits/{id}/ - попытка обновить чужую привычку"""
        self.client.force_authenticate(user=self.user)
        data = {"place": "Взломанное место"}
        response = self.client.patch(
            f"/api/habits/{self.public_habit.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_habit(self):
        """DELETE /api/habits/{id}/ - удаление своей привычки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit.id).exists())

    def test_get_public_habits(self):
        """GET /api/public-habits/ - получение публичных привычек"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/public-habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Публичная привычка")

    def test_pagination(self):
        """Тест пагинации - 5 записей на страницу"""

        for i in range(10):
            Habit.objects.create(
                user=self.user,
                place=f"Место {i}",
                time=time(8 + i, 0),
                action=f"Привычка {i}",
                duration=60,
            )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertEqual(len(response.data["results"]), 5)

    def test_filter_by_public(self):
        """Тест фильтрации по публичности"""

        Habit.objects.create(
            user=self.user,
            place="Кафе",
            time=time(15, 0),
            action="Публичная привычка",
            duration=90,
            is_public=True,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/habits/?is_public=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertTrue(response.data["results"][0]["is_public"])
