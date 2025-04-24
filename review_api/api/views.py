from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from users.models import User

from .paginations import LimitPageNumberPagination
from .permissions import IsAuthorAdminOrReadOnly, ReadOnlyPermission
from .serializers import UserSerializer


class ReviewUserViewSet(UserViewSet):
    """
    Вьюсет для отображения списка пользователей.
    """

    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
