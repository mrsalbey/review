from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ("pk", "email", "username", "first_name", "last_name", "last_login", "date_joined")
    list_filter = ("email", "username", "last_login", "date_joined", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-last_login",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "email")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
