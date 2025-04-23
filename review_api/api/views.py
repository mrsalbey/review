from django.shortcuts import render
from users.models import User
from djoser.views import UserViewSet
from rest_framework.decorators import action


from .permissions import IsAuthorAdminOrReadOnly, ReadOnlyPermission
from rest_framework.permissions import AllowAny, IsAuthenticated

from .paginations import LimitPageNumberPagination
from .serializers import UserSerializer



class ReviewUserViewSet(UserViewSet):
    """
    Вьюсет для отображения списка пользователей.
    """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

