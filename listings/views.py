from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404, ListCreateAPIView
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
    BookingSerializer, LandlordBookingSerializer,
)
from .permissions import IsLandlord

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
        logger.debug(f"User created: {user.email}, password set: {bool(user.password)}, name: {user.first_name}")

        return Response({
            "message": "User registered successfully",
            "user_id": user.id,
            "name": user.first_name,
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
    permission_classes = [IsLandlord, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Listing.objects.filter(landlord=user)


class ListingListCreateView(ListCreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'landlord':
            raise PermissionDenied("Только арендодатель может создавать объявления.")
        serializer.save(landlord=self.request.user)


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

    @action(detail=False, methods=['post'], url_path='change_status')
    def change_status(self, request):
        booking_id = request.data.get('booking_id')
        new_status = request.data.get('status')

        if not booking_id or not new_status:
            return Response({'error': 'Нужно передать booking_id и status'},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_status not in ['approved', 'rejected']:
            return Response({'error': 'Недопустимый статус'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Бронь не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != booking.listing.landlord:
            return Response({'error': 'Вы не являетесь владельцем этого объявления'},
                            status=status.HTTP_403_FORBIDDEN)

        if new_status == 'approved':
            overlapping = Booking.objects.filter(
                listing=booking.listing,
                status='approved',
                start_date__lt=booking.end_date,
                end_date__gt=booking.start_date
            ).exclude(id=booking.id)

            if overlapping.exists():
                return Response(
                    {"error": "Невозможно подтвердить: уже есть подтверждённая бронь на эти даты."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        booking.status = new_status
        booking.save()
        return Response({'status': new_status, 'booking_id': booking.id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()
        if request.user != booking.tenant:
            return Response({'error': 'Вы не можете отменить чужую бронь.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != 'pending':
            return Response({'error': 'Нельзя отменить уже обработанную бронь.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'cancelled'
        booking.save()
        return Response({'status': 'cancelled'}, status=status.HTTP_200_OK)





