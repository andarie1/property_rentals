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
    my_account, register_choice, tenant_dashboard, landlord_dashboard, toggle_listing_status, edit_review,
    create_booking, tenant_bookings, cancel_booking,
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
    path('listings/<int:id>/toggle/', toggle_listing_status, name='toggle_listing_status'),

    # Аутентификация
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/tenant/', tenant_register, name='register_tenant'),
    path('register/landlord/', landlord_register, name='register_landlord'),
    path('my_account/', my_account, name='my_account'),
    path('register_choice/', register_choice, name='register_choice'),
    path('landlord_dashboard/', landlord_dashboard, name='landlord_dashboard'),

    path('dashboard/tenant/', tenant_dashboard, name='tenant_dashboard'),
    path('dashboard/landlord/', landlord_dashboard, name='landlord_dashboard'),

    path('reviews/<int:id>/edit/', edit_review, name='edit_review'),

    # API маршруты
    path('api/', include(router.urls)),

    # JWT токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

urlpatterns += [
    path('booking/<int:listing_id>/create/', create_booking, name='create_booking'),
    path('bookings/', tenant_bookings, name='tenant_bookings'),
    path('booking/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'),
]


