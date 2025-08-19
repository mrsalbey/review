from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, permissions, serializers, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from reviews.models import Review, ReviewCategory, Student
from users.models import User

from .filters import ReviewFilter
from .paginations import LimitPageNumberPagination
from .permissions import IsAuthorAdminOrReadOnly, ReadOnlyPermission
from .serializers import (
    ReviewCategorySerializer,
    ReviewCreateUpdateSerializer,
    ReviewSerializer,
    StudentSerializer,
    UserSerializer,
)


class ThrottleStatusView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        results = {}

        for throttle_class in self.throttle_classes:
            throttle = throttle_class()
            allowed = throttle.allow_request(request, None)

            results[throttle.scope] = {
                "allowed": allowed,
                "wait_seconds": throttle.wait() or 0,
                "rate": throttle.get_rate(),
                "remaining": throttle.num_requests - len(throttle.history),
                "user": request.user.username,
            }

        return Response(results)


class ReviewUserViewSet(UserViewSet):
    """
    Вьюсет для отображения списка пользователей.
    """

    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    throttle_classes = [UserRateThrottle]


class StudentViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = Student.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    throttle_classes = [UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return StudentSerializer
        return StudentSerializer


class ReviewCategoryViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [AllowAny]
    queryset = ReviewCategory.objects.all()
    serializer_class = ReviewCategorySerializer
    pagination_class = None
    throttle_classes = [UserRateThrottle]


class ReviewViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthorAdminOrReadOnly]
    queryset = Review.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ReviewFilter
    throttle_classes = [UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReviewSerializer
        return ReviewCreateUpdateSerializer

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise serializers.ValidationError("Authentication required to create reviews")
        serializer.save(user=self.request.user)
