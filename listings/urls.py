from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('listings/', PublicListingListView.as_view(), name='public-listings'),

    path('listings/mine/', LandlordListingListView.as_view(), name='landlord-listings'),
    path('listings/<int:pk>/', ListingManageView.as_view(), name='listing-manage'),

    path('listings/<int:listing_id>/reviews/', ListingReviewListCreateView.as_view(), name='list-create-review'),

] + router.urls


