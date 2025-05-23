from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "email", "username", "first_name", "last_name")
    list_filter = ("email", "username")
