from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from habbits.paginators import HabitPaginator
from users.models import CustomUser
from users.permissions import IsManager, IsUserSelf
from users.serializers import CustomUserSerializer, RegisterSerializer


class CustomUserListAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.filter(is_staff=False)
    permission_classes = [IsAuthenticated, IsManager]
    pagination_class = HabitPaginator


class CustomUserCreateAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsUserSelf]


class CustomUserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsUserSelf]


class CustomUserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsUserSelf]
