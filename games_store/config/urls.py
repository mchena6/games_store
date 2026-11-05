from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from store.serializers import CustomTokenObtainPairView

from .routers import router

from store.views import CreatePreferenceView, MercadoPagoWebhookView, WelcomeView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    path("api/users/", include("users.urls")),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(), name="swagger_ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(), name="redoc"),

    path("api/checkout/preference/", CreatePreferenceView.as_view(), name="checkout_preference"),
    path("api/checkout/webhook/", MercadoPagoWebhookView.as_view(), name="checkout_webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)