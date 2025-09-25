import uuid

from django.db import transaction
from django.db.models import Count
from rest_framework import serializers

from reviews.models import Review, ReviewCategory, ReviewMetadata, Student
from users.models import User

ALL_FIELDS = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """

    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name")

    def validate_email(self, value):
        """Email должен быть уникальным."""
        lower_email = value.lower()
        if User.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError("Не верный e-mail")
        return lower_email

    def validate_username(self, value):
        """Использовать имя 'me' в качестве username запрещено."""
        if value.lower() == "me":
            raise serializers.ValidationError("Нельзя использовать me")
        return value


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ("id", "name")


class ReviewCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewCategory
        fields = ("id", "name", "slug")


class ReviewSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    category = ReviewCategorySerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "project_id", "created_at", "student", "category")


class ReviewShortSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("id", "project_id", "created_at", "student", "category")

    def get_student(self, obj):
        # Возвращаем только имя студента
        return obj.student.name

    def get_category(self, obj):
        # Возвращаем только slug категории
        return obj.category.slug


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    student = serializers.JSONField(write_only=True)
    category = serializers.JSONField(write_only=True)

    class Meta:
        model = Review
        fields = ("id", "project_id", "student", "category", "created_at")
        read_only_fields = ("id", "created_at", "user")
        extra_kwargs = {
            "project_id": {"required": True, "help_text": "36-символьный UUID проекта (с дефисами)"},
        }

    def validate(self, data):
        # Валидация project_id как UUID
        try:
            uuid.UUID(data["project_id"])
        except (ValueError, TypeError):
            raise serializers.ValidationError({"project_id": "Должен быть валидный UUID (36 символов с дефисами)"})

        # Валидация student
        if "student" not in data or "id" not in data["student"]:
            raise serializers.ValidationError({"student": "Требуется ID студента"})

        try:
            student_id = uuid.UUID(data["student"]["id"])
            if not Student.objects.filter(id=student_id).exists() and "name" not in data["student"]:
                raise serializers.ValidationError({"student": "Студент не найден и не указано имя для создания нового"})
        except (ValueError, TypeError):
            raise serializers.ValidationError({"student": "Некорректный формат UUID студента"})

        # Валидация category
        if "category" not in data or "slug" not in data["category"]:
            raise serializers.ValidationError({"category": "Требуется slug категории"})

        if not ReviewCategory.objects.filter(slug=data["category"]["slug"]).exists():
            raise serializers.ValidationError({"category": "Категория с указанным slug не найдена"})

        return data

    def create_or_get_student(self, student_data):
        try:
            student_id = uuid.UUID(student_data["id"])
            student, created = Student.objects.get_or_create(
                id=student_id, defaults={"name": student_data["name"]} if "name" in student_data else {}
            )
            if not created and "name" in student_data:
                student.name = student_data["name"]
                student.save()
            return student
        except (ValueError, TypeError):
            raise serializers.ValidationError({"student": "Некорректный формат UUID студента"})

    def create(self, validated_data):
        student_data = validated_data.pop("student")
        category_data = validated_data.pop("category")

        student = self.create_or_get_student(student_data)

        review = Review.objects.create(
            project_id=validated_data["project_id"],
            student=student,
            category=ReviewCategory.objects.get(slug=category_data["slug"]),
            user=self.context["request"].user,
        )
        return review

    def update(self, instance, validated_data):
        if "student" in validated_data:
            student_data = validated_data.pop("student")
            instance.student = self.create_or_get_student(student_data)

        if "category" in validated_data:
            instance.category = ReviewCategory.objects.get(slug=validated_data["category"]["slug"])

        if "project_id" in validated_data:
            instance.project_id = validated_data["project_id"]

        instance.save()
        return instance


class BulkReviewSerializer(serializers.ListSerializer):
    child = ReviewCreateUpdateSerializer()

    def validate(self, data):
        for item in data:
            serializer = ReviewCreateUpdateSerializer(data=item, context=self.context)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
        return data

    def create(self, validated_data):
        reviews = []
        for item in validated_data:
            serializer = ReviewCreateUpdateSerializer(context=self.context)
            review = serializer.create(item)
            reviews.append(review)
        return reviews

    def to_representation(self, instance):
        return ReviewShortSerializer(instance, many=True).data
