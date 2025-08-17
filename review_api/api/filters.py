from django_filters.rest_framework import FilterSet, UUIDFilter

from reviews.models import Review


class ReviewFilter(FilterSet):
    project_id = UUIDFilter(field_name="project_id", lookup_expr="exact")

    class Meta:
        model = Review
        fields = ["student", "project_id"]
