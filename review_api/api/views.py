import os
import re
import uuid
from datetime import datetime

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import serializers, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from reviews.models import Review, ReviewCategory, Student
from users.models import User

from .filters import ReviewFilter
from .paginations import LimitPageNumberPagination
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (
    BulkReviewSerializer,
    ReviewCategorySerializer,
    ReviewCreateUpdateSerializer,
    ReviewSerializer,
    ReviewShortSerializer,
    StudentSerializer,
    UserSerializer,
)


class UploadDTFileView(APIView):
    """
    Эндпоинт для загрузки .dt файлов
    """

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle]

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ в байтах
    CHUNK_SIZE = 8192  # 8KB chunks для контроля памяти

    def post(self, request, *args, **kwargs):
        # Проверяем, что файл присутствует в запросе
        if "file" not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES["file"]

        # Проверяем расширение файла
        if not file.name.endswith(".dt"):
            return Response({"error": "Only .dt files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем размер файла
        if file.size > self.MAX_FILE_SIZE:
            return Response(
                {
                    "error": "File size exceeds maximum allowed size of 5 MB",
                    "max_size_mb": 5,
                    "actual_size_mb": round(file.size / (1024 * 1024), 2),
                    "actual_size_bytes": file.size,
                },
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        # Создаем папку uploads если её нет
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # Генерируем уникальное имя файла
        filename = self.generate_unique_filename(file.name)
        file_path = os.path.join(upload_dir, filename)

        try:
            total_written = 0

            with open(file_path, "wb+") as destination:
                for chunk in file.chunks(self.CHUNK_SIZE):
                    # Дополнительная проверка во время записи
                    total_written += len(chunk)
                    if total_written > self.MAX_FILE_SIZE:
                        # Удаляем частично записанный файл
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        return Response(
                            {"error": "File size exceeds limit during upload"},
                            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        )
                    destination.write(chunk)

            # Финальная проверка размера
            actual_size = os.path.getsize(file_path)
            if actual_size > self.MAX_FILE_SIZE:
                os.remove(file_path)
                return Response(
                    {"error": "Uploaded file exceeds size limit"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )

            return Response(
                {
                    "message": "File uploaded successfully",
                    "filename": filename,
                    "original_filename": file.name,
                    "size": actual_size,
                    "size_mb": round(actual_size / (1024 * 1024), 2),
                    "path": file_path,
                    "user": request.user.username,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            # Удаляем файл в случае ошибки
            if os.path.exists(file_path):
                os.remove(file_path)
            return Response({"error": f"File upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_unique_filename(self, original_filename):
        """
        Генерирует уникальное имя файла чтобы избежать конфликтов
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        name, ext = os.path.splitext(original_filename)

        # Убираем пробелы из имени файла
        name = re.sub(r"[^\w\.-]", "_", name)

        return f"{name}_{timestamp}_{unique_id}{ext}"


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
            if self.action == "list":
                return ReviewShortSerializer
            else:
                return ReviewSerializer
        if self.action == "bulk_create":
            return BulkReviewSerializer
        return ReviewCreateUpdateSerializer

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise serializers.ValidationError("Для создания ревью необходимо авторизоваться")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk", throttle_classes=[UserRateThrottle])
    def bulk_create(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Ожидается список объектов"}, status=status.HTTP_400_BAD_REQUEST)

        if len(request.data) > 50:
            return Response({"error": "Максимальное количество элементов - 50"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Сохраняем объекты
        reviews = serializer.save()

        # Возвращаем ответ через сериализатор (уже в кратком формате)
        return Response(
            {"message": f"Успешно создано {len(reviews)} ревью", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
