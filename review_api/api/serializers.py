from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import User
from reviews.models import Student, Review, ReviewCategory, ReviewMetadata

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
        fields = ("id", "name", "slug", "description")


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ("id", "student", "user", "project_id", "category")

    def validate_project_id(self, value):
        pass


class ReviewMetadataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReviewMetadata
        fields = ("id", "review", "full_name", "object_id")

    def validate_project_id(self, value):
        pass
