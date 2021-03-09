from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import (
    CreateUserView,
    UpdateUserView,
    ChangePasswordView,
    CurrentUserLocationView
)


urlpatterns = [
    path('login/', TokenObtainPairView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),
    path('register/', CreateUserView.as_view()),
    path('change_password/<int:pk>/', ChangePasswordView.as_view()),
    path('update_user_info/<int:pk>/', UpdateUserView.as_view()),
    path('location/', CurrentUserLocationView.as_view())
]
