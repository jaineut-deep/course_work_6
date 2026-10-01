from datetime import datetime, time
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.test import APIClient
from rest_framework.response import Response as DRFResponse
from unittest.mock import patch
from .models import Habit, HabitCompletion
from .serializers import HabitSerializer, HabitCompletionSerializer
from .mixins import FullCleanMixin
from users.models import CustomUser


class TestHabitSerializer(FullCleanMixin, HabitCompletionSerializer):
    pass


class HabitTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username="user_test", email="test@example.com", password="qwerty")
        self.user_owner = CustomUser.objects.create_user(
            username="owner_user", email="owner@example.com", password="123qwe"
        )
        self.user_moder = CustomUser.objects.create_user(
            username="moder_user", email="moder@example.com", password="qwe123", is_staff=True
        )
        self.habit_one = Habit.objects.create(
            place="Стадион 'Локомотив'",
            time=time(12, 0, 0),
            action="бег по кругу",
            periodicity="two_days",
            duration=120,
            is_public=True,
            is_enjoyable=False,
            reward="купить шашлык",
            related_habit=None,
            owner=self.user,
        )
        self.habit_two = Habit.objects.create(
            place="Областная библиотека",
            time=time(10, 0, 0),
            action="выбрать интересные книги из буккроссинга",
            periodicity="daily",
            duration=120,
            is_public=False,
            is_enjoyable=True,
            reward="",
            related_habit=None,
            owner=self.user,
        )
        self.habit_three = Habit.objects.create(
            place="Дом",
            time=time(9, 0, 0),
            action="уборка комнаты",
            periodicity="two_days",
            duration=120,
            is_public=True,
            is_enjoyable=False,
            reward="",
            related_habit=self.habit_two,
            owner=self.user,
        )
        self.habit_completed_one = HabitCompletion.objects.create(
            habit=self.habit_one,
            completed_at=datetime(2026, 9, 22, 12, 2, 0),
            is_completed=True,
            note="Приятная безоблачная погода",
        )

        self.client: APIClient = APIClient()

    @patch.object(HabitCompletion, 'clean', return_value=None)
    def test_habit_completion_create(self, mock_clean):
        self.client.force_authenticate(user=self.user)
        url = reverse("habbits:habit_completion_create")
        data = {
            "habit": self.habit_one.pk,
            "completed_at": datetime(2026, 9, 24, 12, 2, 0),
            "is_completed": True,
            "note": "Был дождь :(((",
        }
        response = self.client.post(url, data)
        habit_completion_data = HabitCompletion.objects.get(
            habit=self.habit_one.pk, note="Был дождь :((("
        )
        serialized_habit_completion = TestHabitSerializer(habit_completion_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_habit_completion.data)

    def test_habit_completion_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("habbits:habit_completion_list")
        response : DRFResponse = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)

        habit_data = HabitCompletion.objects.filter(habit__owner=self.user)
        serialized_habit = HabitCompletionSerializer(habit_data, many=True)

        page_size = response.data.get("page_size", 5)
        expected_count = min(len(serialized_habit.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_habit_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("habbits:habit_create")
        data = {
            "place": "Комната дома",
            "time": time(8, 0, 0),
            "action": "зарядка",
            "periodicity": "two_days",
            "duration": 120,
            "is_public": True,
            "is_enjoyable": False,
            "reward": "",
            "related_habit": self.habit_two.pk,
            "owner": self.user,
        }
        response = self.client.post(url, data)
        habit_data = Habit.objects.get(place="Комната дома", reward="")
        serialized_habit = HabitSerializer(habit_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_habit.data)

    def test_habit_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("habbits:habit_list")
        response : DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)

        habit_data = Habit.objects.filter(owner=self.user)
        serialized_habit = HabitSerializer(habit_data, many=True)

        page_size = response.data.get("page_size", 5)
        expected_count = min(len(serialized_habit.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_habit_retrieve(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("habbits:habit_retrieve", args=(self.habit_one.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("place"), self.habit_one.place)

    def test_habit_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("habbits:habit_update", args=(self.habit_three.pk,))
        data = {
            "time": time(8, 20, 0),
            "duration": 100,
        }
        response = self.client.patch(url, data)
        data_output = response.json()
        self.habit_three.refresh_from_db()
        serialized_habit = HabitSerializer(self.habit_three)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(data_output.get("duration"), serialized_habit.data.get("duration"))

    def test_habit_destroy(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("habbits:habit_delete", args=(self.habit_three.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(owner=self.user).count(), 2)

    def test_habit_public_list(self):
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habbits:habit_public_list")
        response : DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)

        habit_data = Habit.objects.filter(is_public=True)
        serialized_habit = HabitSerializer(habit_data, many=True)

        page_size = response.data.get("page_size", 5)
        expected_count = min(len(serialized_habit.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def tearDown(self):
        CustomUser.objects.get(username="user_test").delete()
        CustomUser.objects.get(username="owner_user").delete()
        CustomUser.objects.get(username="moder_user").delete()
