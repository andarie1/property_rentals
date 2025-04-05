from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet,
    home,
    listing_list,
    listing_detail,
    create_listing,
    login_view,
    logout_view,
    tenant_register,
    landlord_register,
    my_account, register_choice
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register(r'listings', ListingViewSet)  # API маршруты

urlpatterns = [
    # Главная
    path('', home, name='home'),

    # Объявления
    path('listings/', listing_list, name='listing_list'),
    path('listings/<int:id>/', listing_detail, name='listing_detail'),
    path('listings/create/', create_listing, name='create_listing'),

    # Аутентификация
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/tenant/', tenant_register, name='register_tenant'),
    path('register/landlord/', landlord_register, name='register_landlord'),
    path('my_account/', my_account, name='my_account'),
    path('register_choice/', register_choice, name='register_choice'),

    # API маршруты
    path('api/', include(router.urls)),

    # JWT токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]




