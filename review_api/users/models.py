from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

USERNAME_VALIDATOR = RegexValidator(regex="^[\\w.@+-]+$", message="Invalid username")


class User(AbstractUser):
    """
    Собственный класс для пользователей приложения.
    """

    email = models.EmailField(max_length=254, unique=True, blank=False, verbose_name="Email")
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Имя пользователя",
        validators=[USERNAME_VALIDATOR],
    )
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    first_name = models.CharField(max_length=150, verbose_name="Имя")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username
