from django.urls import path
from .views import RegisterAPIView, MeAPIView, UserManagementViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("users", UserManagementViewSet, basename='users')

urlpatterns = [
	path('register/', RegisterAPIView.as_view(), name='register'),
	path('login/', TokenObtainPairView.as_view(), name='login'),
	path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('me/', MeAPIView.as_view(), name='me'),
] + router.urls