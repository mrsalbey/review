from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    #path("redoc/", TemplateView.as_view(template_name="redoc.html"), name="redoc"),
    # Генерация схемы OpenAPI
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI (альтернативный интерфейс)
    path('api/v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ReDoc (основной интерфейс)
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
