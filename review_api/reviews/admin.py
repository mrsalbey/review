import uuid

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Review, ReviewCategory, ReviewMetadata, Student


class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "created_at")
    search_fields = ("name", "id")
    readonly_fields = ("id", "created_at")
    list_filter = ("created_at",)
    ordering = ("name",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["id"].help_text = "UUID студента (генерируется автоматически)"
        return form


class ReviewCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("id", "created_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "description")}),
        ("Системная информация", {"fields": ("id", "created_at"), "classes": ("collapse",)}),
    )


class ReviewMetadataInline(admin.TabularInline):
    model = ReviewMetadata
    extra = 0
    readonly_fields = ("id", "created_at")
    fields = ("full_name", "object_id", "created_at")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = "__all__"

    def clean_project_id(self):
        project_id = self.cleaned_data["project_id"]
        try:
            uuid.UUID(project_id)
        except ValueError:
            raise ValidationError("Неверный формат UUID. Ожидается 36-символьный идентификатор с дефисами")
        return project_id


class ReviewAdmin(admin.ModelAdmin):
    form = ReviewForm
    list_display = ("project_id", "student", "category", "user", "created_at")
    list_filter = ("category", "created_at", "user")
    search_fields = ("project_id", "student__name")
    readonly_fields = ("id", "created_at")
    raw_id_fields = ("student", "user")
    inlines = (ReviewMetadataInline,)
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("project_id", "student", "user", "category")}),
        ("Системная информация", {"fields": ("id", "created_at"), "classes": ("collapse",)}),
    )


class ReviewMetadataAdmin(admin.ModelAdmin):
    list_display = ("full_name", "object_id", "review_link", "created_at")
    search_fields = ("full_name", "object_id", "review__project_id")
    readonly_fields = ("id", "created_at", "review_link")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"

    def review_link(self, obj):
        return obj.review

    review_link.short_description = "Ревью"
    review_link.admin_order_field = "review__project_id"


admin.site.register(Student, StudentAdmin)
admin.site.register(ReviewCategory, ReviewCategoryAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewMetadata, ReviewMetadataAdmin)
