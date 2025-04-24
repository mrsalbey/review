import uuid

from django.core.validators import RegexValidator
from django.db import models

from users.models import User

uuid_validator = RegexValidator(
    regex="^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    message='Введите корректный UUID в формате: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"',
    code="invalid_uuid",
)


def generate_uuid():
    return str(uuid.uuid4())


class Student(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,  # 32 символа + 4 дефиса
        default=generate_uuid,
        editable=False,
        unique=True,
        verbose_name="UUID идентификатор",
        validators=[uuid_validator],
        db_index=True,
    )
    name = models.CharField(max_length=150, verbose_name="Имя студента")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ["name"]


class ReviewCategory(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Уникальный идентификатор категории"
    )
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название категории", help_text="Например: Диплом, Мобильный, Спринт"
    )
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-идентификатор", blank=True)
    description = models.TextField(blank=True, verbose_name="Описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория проектов"
        verbose_name_plural = "Категории проектов"
        ordering = ["name"]


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Уникальный ID ревью")
    student = models.ForeignKey("Student", on_delete=models.CASCADE, verbose_name="Студент", related_name="reviews")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь системы", related_name="reviews"
    )
    project_id = models.CharField(
        max_length=36, verbose_name="ID проекта", help_text="36-символьный UUID проекта (с дефисами)"
    )
    category = models.ForeignKey("ReviewCategory", on_delete=models.PROTECT, verbose_name="Категория проекта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Ревью {self.project_id} ({self.student.name})"

    class Meta:
        verbose_name = "Ревью проекта"
        verbose_name_plural = "Ревью проектов"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project_id"]),
            models.Index(fields=["created_at"]),
        ]


class ReviewMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Уникальный ID метаданных")
    review = models.ForeignKey(
        "Review", on_delete=models.CASCADE, verbose_name="Связанное ревью", related_name="metadata_items"
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name="Полное имя метаданных",
    )
    object_id = models.CharField(
        max_length=36,
        verbose_name="Идентификатор объекта метаданных",
        validators=[uuid_validator],
        help_text="Формат: 8-4-4-4-12 hex-символов (с дефисами)",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")

    class Meta:
        verbose_name = "Метаданные ревью"
        verbose_name_plural = "Метаданные ревью"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["review"]),
            models.Index(fields=["object_id"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.object_id})"
