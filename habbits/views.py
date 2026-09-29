from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from habbits.models import Habit, HabitCompletion
from habbits.serializers import HabitSerializer, HabitCompletionSerializer
from habbits.paginators import HabitPaginator
from users.permissions import IsNotManager, IsOwner


class HabitCompletionListAPIView(generics.ListAPIView):
    serializer_class = HabitCompletionSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = HabitCompletion.objects.all().order_by("id")
    pagination_class = HabitPaginator


class HabitCreateAPIView(generics.CreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsNotManager]

    @extend_schema(summary="Метод для создания нового объекта привычки")
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all().order_by("id")
    pagination_class = HabitPaginator


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all()


class HabitUpdateAPIView(generics.UpdateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all()


class HabitDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all()


class HabitPublicListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    queryset = Habit.objects.filter(is_public=True)
    pagination_class = HabitPaginator
