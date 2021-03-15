from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import (
    CreateUserView,
    UpdateUserView,
    ChangePasswordView,
    CurrentUserLocationView,
    UserDetailView,
    ProposalsListView,
    MatchedListView,
    SwipeView,
    ChatViewSet
)

router = DefaultRouter()
router.register('chat', ChatViewSet, basename='chat')

urlpatterns = router.urls + [
    path('login/', TokenObtainPairView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),
    path('register/', CreateUserView.as_view()),
    path('change_password/<int:pk>/', ChangePasswordView.as_view()),
    path('update_user_info/<int:pk>/', UpdateUserView.as_view()),
    path('location/', CurrentUserLocationView.as_view()),
    path('user/<int:pk>/', UserDetailView.as_view()),
    path('proposals/', ProposalsListView.as_view()),
    path('matched/', MatchedListView.as_view()),
    path('swipe/<int:pk>/', SwipeView.as_view())
]
