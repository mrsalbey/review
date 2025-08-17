from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ReviewCategoryViewSet, ReviewUserViewSet, ReviewViewSet,
                    StudentViewSet)

router = DefaultRouter()

router.register("users", ReviewUserViewSet, basename="users")
router.register("students", StudentViewSet, basename="students")
router.register("categories", ReviewCategoryViewSet, basename="categories")
router.register("reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    path("v1/auth/", include("djoser.urls")),
    path("v1/auth/", include("djoser.urls.authtoken")),
    path("v1/", include(router.urls)),
]
