from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

import logging

from .models import Listing, Review, Booking
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ListingSerializer,
    ReviewSerializer,
    BookingSerializer
)
from .permissions import IsLandlord, IsTenant

logger = logging.getLogger(__name__)
User = get_user_model()

# ---------------------- Auth ----------------------

class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"User created: {user.email} (Role: {user.role})")

        return Response({
            "message": "User registered successfully",
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class CustomLoginView(TokenObtainPairView):
    """Пользовательский логин с JWT."""
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """Выход пользователя с блокировкой refresh-токена."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs) -> Response:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Выход выполнен"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ---------------------- Listings ----------------------

class PublicListingListView(generics.ListAPIView):
    """Список активных объявлений для всех пользователей."""
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
    """Объявления текущего арендодателя."""
    serializer_class = ListingSerializer
    permission_classes = [IsLandlord, IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Listing.objects.none()
        return Listing.objects.filter(landlord=self.request.user)


class ListingListCreateView(ListCreateAPIView):
    """Создание и просмотр всех объявлений (для landlord)."""
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsLandlord, IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user)


class ListingManageView(RetrieveUpdateDestroyAPIView):
    """Обновление, удаление, переключение активности объявлений."""
    serializer_class = ListingSerializer
    permission_classes = [IsLandlord]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Listing.objects.none()
        return Listing.objects.filter(landlord=self.request.user)

    def patch(self, request, *args, **kwargs) -> Response:
        listing = self.get_object()
        if request.data.get("toggle_status"):
            listing.is_active = not listing.is_active
            listing.save()
            logger.info(f"Listing status toggled: {listing.id} — {listing.is_active}")
            return Response({
                "status": "updated",
                "is_active": listing.is_active
            }, status=status.HTTP_200_OK)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs) -> Response:
        listing = self.get_object()
        listing_title = listing.title
        listing.delete()
        logger.warning(f"Listing deleted: {listing_title} (ID: {listing.id})")
        return Response({
            "status": "deleted",
            "message": f"Listing '{listing_title}' has been successfully deleted"
        }, status=status.HTTP_200_OK)

# ---------------------- Reviews ----------------------

class ListingReviewListCreateView(generics.ListCreateAPIView):
    """Отзывы к конкретному объявлению. Только tenant может оставить 1 отзыв после брони."""
    serializer_class = ReviewSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()] if self.request.method == 'POST' else [permissions.AllowAny()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(listing_id=self.kwargs['listing_id'])

    def perform_create(self, serializer):
        user = self.request.user
        listing_id = self.kwargs.get('listing_id')
        listing = get_object_or_404(Listing, id=listing_id)

        if user.role != 'tenant':
            raise PermissionDenied("Только съёмщики могут оставлять отзывы.")

        if Review.objects.filter(tenant=user, listing=listing).exists():
            raise PermissionDenied("Вы уже оставили отзыв к этому объявлению.")

        if not Booking.objects.filter(tenant=user, listing=listing, status='approved').exists():
            raise PermissionDenied("Только после подтверждённой брони можно оставить отзыв.")

        serializer.save(tenant=user, listing=listing)

# ---------------------- Bookings ----------------------

class BookingViewSet(viewsets.ModelViewSet):
    """Работа с бронями: создание, просмотр, подтверждение, отклонение, отмена."""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsTenant()]
        elif self.action in ['update', 'partial_update', 'change_status']:
            return [IsLandlord()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        if user.role == 'tenant':
            return Booking.objects.filter(tenant=user)
        elif user.role == 'landlord':
            return Booking.objects.filter(listing__landlord=user)
        return Booking.objects.none()

    @action(detail=False, methods=['post'], url_path='change_status')
    def change_status(self, request) -> Response:
        booking_id = request.data.get('booking_id')
        new_status = request.data.get('status')

        if not booking_id or not new_status:
            return Response({'error': 'Нужно передать booking_id и status'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in ['confirmed', 'cancelled']: # statuses modified as per model's
            return Response({'error': 'Недопустимый статус'}, status=status.HTTP_400_BAD_REQUEST)

        booking = get_object_or_404(Booking, id=booking_id)

        if booking.listing.landlord != request.user:
            return Response({'error': 'Вы не владелец этого объявления'}, status=status.HTTP_403_FORBIDDEN)

        if new_status == 'approved':
            overlap = Booking.objects.filter(
                listing=booking.listing,
                status='approved',
                start_date__lt=booking.end_date,
                end_date__gt=booking.start_date
            ).exclude(id=booking.id)
            if overlap.exists():
                return Response({'error': 'Невозможно подтвердить: пересечение с другой бронью.'},
                                status=status.HTTP_400_BAD_REQUEST)

        booking.status = new_status
        booking.save()
        logger.info(f"Booking status updated: {booking.id} — {new_status}")
        return Response({'status': new_status, 'booking_id': booking.id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None) -> Response:
        booking = self.get_object()
        if request.user != booking.tenant:
            return Response({'error': 'Вы не можете отменить чужую бронь.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != 'pending':
            return Response({'error': 'Нельзя отменить уже обработанную бронь.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'cancelled'
        booking.save()
        logger.info(f"Booking cancelled: {booking.id}")
        return Response({'status': 'cancelled'}, status=status.HTTP_200_OK)
