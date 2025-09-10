import uuid

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import serializers, status, viewsets
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
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (BulkReviewSerializer, ReviewCategorySerializer,
                          ReviewCreateUpdateSerializer, ReviewSerializer,
                          StudentSerializer, UserSerializer)


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
        if self.action == "bulk_create":
            return BulkReviewSerializer
        return ReviewCreateUpdateSerializer

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise serializers.ValidationError("Authentication required to create reviews")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk", throttle_classes=[UserRateThrottle])
    def bulk_create(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Ожидается список объектов"}, status=status.HTTP_400_BAD_REQUEST)

        if len(request.data) > 50:
            return Response({"error": "Максимальное количество элементов - 50"}, status=status.HTTP_400_BAD_REQUEST)

        # Валидируем каждый элемент
        validated_data = []
        errors = []

        for i, item in enumerate(request.data):
            serializer = ReviewCreateUpdateSerializer(data=item, context={"request": request})
            if serializer.is_valid():
                validated_data.append(serializer.validated_data)
            else:
                errors.append({"index": i, "errors": serializer.errors})

        if errors:
            return Response({"error": "Ошибки валидации", "details": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем объекты
        reviews_to_create = []
        for item in validated_data:
            student_data = item.pop("student")
            category_data = item.pop("category")

            student = self.create_or_get_student(student_data)
            category = ReviewCategory.objects.get(slug=category_data["slug"])

            reviews_to_create.append(
                Review(project_id=item["project_id"], student=student, category=category, user=request.user)
            )

        # Массовое создание
        created_reviews = Review.objects.bulk_create(reviews_to_create)

        return Response(
            {
                "message": f"Успешно создано {len(created_reviews)} ревью",
                "data": ReviewSerializer(created_reviews, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def create_or_get_student(self, student_data):
        # Ваша существующая логика из сериализатора
        try:
            student_id = uuid.UUID(student_data["id"])
            student, created = Student.objects.get_or_create(
                id=student_id, defaults={"name": student_data.get("name", "")}
            )
            if not created and "name" in student_data:
                student.name = student_data["name"]
                student.save()
            return student
        except (ValueError, TypeError):
            raise serializers.ValidationError({"student": "Некорректный формат UUID студента"})
