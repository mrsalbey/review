from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter

from .views import (ReviewCategoryViewSet, ReviewUserViewSet, ReviewViewSet,
                    StudentViewSet, ThrottleStatusView)

router = DefaultRouter()

router.register("users", ReviewUserViewSet, basename="users")
router.register("students", StudentViewSet, basename="students")
router.register("categories", ReviewCategoryViewSet, basename="categories")
router.register("reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    path("v1/auth/", include("djoser.urls")),
    path("v1/auth/", include("djoser.urls.authtoken")),
    path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("v1/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("v1/throttle-status/", ThrottleStatusView.as_view(), name="throttle-status"),
    path("v1/", include(router.urls)),
]
