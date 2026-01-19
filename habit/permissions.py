from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение только для владельца объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение на чтение для всех, на запись только для владельца"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsPublicOrOwner(permissions.BasePermission):
    """Разрешение на чтение публичных привычек или своих привычек"""

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user

        return obj.user == request.user
