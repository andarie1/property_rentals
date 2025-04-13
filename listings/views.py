from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
import logging

from .models import Listing, Review, Booking
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ListingSerializer,
    ReviewSerializer,
    BookingSerializer,
)
from .permissions import IsLandlord, CanReviewListing

logger = logging.getLogger(__name__)

User = get_user_model()

# ---------------- Auth ----------------

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.debug(f"User created: {user.username}, password set: {bool(user.password)}")

        return Response({
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Выход выполнен"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ---------------- Listings ----------------

class PublicListingListView(generics.ListAPIView):
    queryset = Listing.objects.filter(is_active=True)
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = {
        'rooms': ['exact'],
        'housing_type': ['exact'],
        'price': ['gte', 'lte'],
    }

    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price', 'created_at']


class LandlordListingListView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsLandlord]

    def get_queryset(self):
        return Listing.objects.filter(landlord=self.request.user)


class ListingManageView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsLandlord]

    def get_queryset(self):
        return Listing.objects.filter(landlord=self.request.user)

    def patch(self, request, *args, **kwargs):
        if request.data.get("toggle_status"):
            listing = self.get_object()
            listing.is_active = not listing.is_active
            listing.save()
            return Response({
                "status": "updated",
                "is_active": listing.is_active
            }, status=status.HTTP_200_OK)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        listing = self.get_object()
        title = listing.title
        listing.delete()
        return Response({
            "status": "deleted",
            "message": f"Listing '{title}' has been successfully deleted"
        }, status=status.HTTP_200_OK)


class ListingReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Review.objects.filter(listing_id=self.kwargs['listing_id'])

    def perform_create(self, serializer):
        user = self.request.user
        listing_id = self.kwargs.get('listing_id')
        if not listing_id:
            raise ValidationError("Listing ID is missing in URL.")
        listing = get_object_or_404(Listing, id=listing_id)

        if user.role != 'tenant':
            raise PermissionDenied("Только съёмщики могут оставлять отзывы.")

        already_reviewed = Review.objects.filter(tenant=user, listing_id=listing_id).exists()
        if already_reviewed:
            raise PermissionDenied("Вы уже оставили отзыв к этому объявлению.")

        has_approved_booking = Booking.objects.filter(
            tenant=user,
            listing_id=listing_id,
            status='approved'
        ).exists()

        if not has_approved_booking:
            raise PermissionDenied("Вы можете оставить отзыв только после подтверждённой брони.")

        serializer.save(tenant=user, listing=listing)

# ---------------- Booking ----------------

class IsTenant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tenant'


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsTenant()]
        elif self.action in ['update', 'partial_update', 'approve', 'reject']:
            return [IsLandlord()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'tenant':
            return Booking.objects.filter(tenant=user)
        elif user.role == 'landlord':
            return Booking.objects.filter(listing__landlord=user)
        return Booking.objects.none()

    @action(detail=True, methods=['post'], url_path='change_status')
    def change_status(self, request, pk=None):
        booking = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = new_status
        booking.save()
        return Response({'status': new_status}, status=status.HTTP_200_OK)




