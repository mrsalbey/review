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
    Разрешает:
    - Чтение всем
    - Изменение только автору
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает:
    - Чтение всем
    - Создание любому авторизованному пользователю
    - Изменение только автору или админу
    """

    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем POST любому авторизованному пользователю
        if request.method == "POST":
            return request.user.is_authenticated

        # Для остальных методов (PUT, PATCH, DELETE) проверяем в has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем изменение только автору или админу
        return obj.user == request.user or request.user.is_superuser
