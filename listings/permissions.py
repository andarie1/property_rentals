from rest_framework import permissions
from listings.models import Booking, Review


class IsLandlord(permissions.BasePermission):
    """
    Разрешает доступ только пользователям с ролью 'landlord'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'landlord'

class IsTenant(permissions.BasePermission):
    """
    Разрешает доступ только пользователям с ролью 'tenant'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tenant'

class CanReviewListing(permissions.BasePermission):
    """
    Разрешает оставлять отзыв только пользователям с ролью 'tenant' один раз, если бронь подтверждена.
    """
    def has_permission(self, request, view):
        user = request.user

        try:
            listing_id = view.kwargs['listing_id']
        except (AttributeError, KeyError):
            return False

        if not user.is_authenticated or user.role != 'tenant':
            return False

        already_reviewed = Review.objects.filter(tenant=user, listing_id=listing_id).exists()
        if already_reviewed:
            return False

        has_approved_booking = Booking.objects.filter(
            tenant=user,
            listing_id=listing_id,
            status='approved'
        ).exists()

        return has_approved_booking


