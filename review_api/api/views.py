from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (exceptions, permissions, serializers, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from reviews.models import Review, ReviewCategory, Student
from users.models import User

from .filters import ReviewFilter
from .paginations import LimitPageNumberPagination
from .permissions import IsAuthorAdminOrReadOnly, ReadOnlyPermission
from .serializers import (ReviewCategorySerializer,
                          ReviewCreateUpdateSerializer, ReviewSerializer,
                          StudentSerializer, UserSerializer)


class ReviewUserViewSet(UserViewSet):
    """
    Вьюсет для отображения списка пользователей.
    """

    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination


class StudentViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = Student.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return StudentSerializer
        return StudentSerializer


class ReviewCategoryViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [AllowAny]
    queryset = ReviewCategory.objects.all()
    serializer_class = ReviewCategorySerializer
    pagination_class = None


class ReviewViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthorAdminOrReadOnly]
    queryset = Review.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ReviewFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReviewSerializer
        return ReviewCreateUpdateSerializer

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise serializers.ValidationError("Authentication required to create reviews")
        serializer.save(user=self.request.user)
