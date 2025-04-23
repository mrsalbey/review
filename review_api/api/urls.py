from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ReviewUserViewSet


router = DefaultRouter()

router.register("users", ReviewUserViewSet, basename="users")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/auth/", include("djoser.urls")),
    path("v1/auth/", include("djoser.urls.authtoken")),
]
