from rest_framework.throttling import UserRateThrottle


class ExtendedUserRateThrottle(UserRateThrottle):
    """
    Кастомный троттлинг с дополнительными возможностями
    """

    scope = "extended_user"  # Уникальный идентификатор для настроек

    def allow_request(self, request, view):
        # Можно добавить кастомную логику проверки
        if request.user.is_superuser:
            return True  # Суперпользователи не ограничены
        return super().allow_request(request, view)
