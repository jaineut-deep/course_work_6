from django.urls import path
from users.apps import UsersConfig
from users.views import (
    CustomUserListAPIView,
    CustomUserCreateAPIView,
    CustomUserRetrieveAPIView,
    CustomUserUpdateAPIView,
    CustomUserDestroyAPIView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name


urlpatterns = [
    # customuser_routes
    path("auth/registry/", CustomUserCreateAPIView.as_view(), name="register_user"),
    path("user/", CustomUserListAPIView.as_view(), name="user_list"),
    path("user/<int:pk>/", CustomUserRetrieveAPIView.as_view(), name="user_retrieve"),
    path("user/update/<int:pk>/", CustomUserUpdateAPIView.as_view(), name="user_update"),
    path("user/delete/<int:pk>/", CustomUserDestroyAPIView.as_view(), name="user_delete"),
    # token_routes
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
