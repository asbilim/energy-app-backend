from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from authentication.views import (
    RegisterView, CustomTokenObtainPairView, LogoutView, dashboard_view,
    login_view, logout_view, register_view
)
from dimensionnement.views import DimensionnementViewSet
from composants.views import ComposantViewSet, composants_management_view

# API Router
router = DefaultRouter()
router.register(r'dimensionnements', DimensionnementViewSet, basename='dimensionnement')
router.register(r'composants', ComposantViewSet, basename='composant')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Web Views
    path('', lambda request: redirect('dashboard'), name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('composants-management/', composants_management_view, name='composants_management'),
    
    # Django Auth Compatibility URLs
    path('accounts/login/', login_view, name='accounts_login'),
    path('accounts/logout/', logout_view, name='accounts_logout'),
    
    # API Authentication
    path('api/auth/register/', RegisterView.as_view(), name='api_register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='api_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='api_logout'),
    
    # API Routes
    path('api/', include(router.urls)),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
