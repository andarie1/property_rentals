from django.utils import timezone
from rest_framework import serializers, request
from django.contrib.auth import get_user_model,authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from listings.models import Listing, Review, Booking

User = get_user_model()

# ---------------- Registration ----------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    name = serializers.CharField(required=True, max_length=30)

    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data['name'],
            role=validated_data.get('role')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# ---------------- Auth ----------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                **{self.username_field: email, "password": password}
            )
            if not user:
                raise serializers.ValidationError(
                    _("No active account found with the given credentials"),
                    code="authorization",
                )

        else:
            raise serializers.ValidationError(
                _("Must include '%s' and 'password'.") % self.username_field,
                code="authorization",
            )

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }

# ---------------- User ----------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

# ---------------- Listing ----------------
class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['id', 'landlord', 'created_at', 'updated_at']

# ---------------- Review ----------------
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        listing = data.get('listing')
        tenant = self.context['request'].user

        approved_booking_exists = Booking.objects.filter(
            listing=listing,
            tenant=tenant,
            status='approved',
            end_date__lt=timezone.now()
        ).exists()

        if not approved_booking_exists:
            raise serializers.ValidationError(
                "Вы не можете оставить отзыв: у вас нет подтверждённой аренды этого жилья."
            )

        return data
# ---------------- Booking ----------------
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['tenant', 'status']

    def validate_start_date(self, value):
        tomorrow = date.today() + timedelta(days=1)
        if value < tomorrow:
            raise serializers.ValidationError("Бронирование возможно только начиная с завтрашнего дня.")
        return value

    def validate(self, data):
        listing = data.get('listing')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date >= end_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала.")

        overlapping = Booking.objects.filter(
            listing=listing,
            status__in='approved',
            start_date__lt=end_date,
            end_date__gt=start_date
        )
        if overlapping.exists():
            raise serializers.ValidationError("Невозможно создать бронь: выбранные даты уже заняты.")

        return data

    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].user
        return super().create(validated_data)


class LandlordBookingSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    location = serializers.CharField(source='listing.location', read_only=True)
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'start_date',
            'end_date',
            'status',
        ]
