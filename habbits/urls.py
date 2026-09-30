from django.urls import path

from habbits.apps import HabbitsConfig
from habbits.views import (HabitCompletionListAPIView, HabitCreateAPIView, HabitDestroyAPIView, HabitListAPIView,
                           HabitPublicListAPIView, HabitRetrieveAPIView, HabitUpdateAPIView)

app_name = HabbitsConfig.name

urlpatterns = [
    path("completed_habit/", HabitCompletionListAPIView.as_view(), name="habit_completion_list"),
    path("habit/", HabitListAPIView.as_view(), name="habit_list"),
    path("habit/create/", HabitCreateAPIView.as_view(), name="habit_create"),
    path("habit/<int:pk>/", HabitRetrieveAPIView.as_view(), name="habit_retrieve"),
    path("habit/update/<int:pk>/", HabitUpdateAPIView.as_view(), name="habit_update"),
    path("habit/delete/<int:pk>/", HabitDestroyAPIView.as_view(), name="habit_delete"),
    path("public_habit/", HabitPublicListAPIView.as_view(), name="habit_public_list"),
]
