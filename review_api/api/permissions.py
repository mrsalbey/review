from rest_framework import permissions


class ReadOnlyPermission(permissions.BasePermission):
    """
    Доступ только на чтение.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class DenyAll(permissions.BasePermission):
    """
    Запрещает доступ к неиспользуемым Djoser-эндпоинтам.
    """

    def has_permission(self, request, view):
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Доступ на изменение только для автора.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.author == request.user


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Доступ на изменение только для автора или админа.
    Доступ на чтение всем остальным.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_superuser or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.author == request.user or obj.user == request.user
