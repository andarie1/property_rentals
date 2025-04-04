from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet, home, listing_list, listing_detail, create_listing, login_register, logout_view
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register(r'listings', ListingViewSet)  # API

urlpatterns = [
    # Основные маршруты
    path('', home, name='home'),
    path('listings/', listing_list, name='listing_list'),
    path('listings/<int:id>/', listing_detail, name='listing_detail'),
    path('listings/create/', create_listing, name='create_listing'),

    # Аутентификация через шаблон
    path('auth/', login_register, name='login_register'),
    path('logout/', logout_view, name='logout'),

    # API
    path('api/', include(router.urls)),

    # JWT авторизация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]


