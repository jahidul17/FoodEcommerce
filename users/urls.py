from django.urls import path, include
from .views import RegisterAPIView, ActivateAPIView, MyTokenObtainPairView, LogoutView, ProfileViewSet,PasswordResetRequestAPIView,PasswordResetConfirmAPIView, ChangePasswordView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", ActivateAPIView.as_view(), name="activate"),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
    path("password-reset/", PasswordResetRequestAPIView.as_view(), name="password_reset"),
    path("password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmAPIView.as_view(), name="password_reset_confirm"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
