from rest_framework.permissions import BasePermission


class IsNotManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        return not request.user.is_staff


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return obj.owner == request.user
