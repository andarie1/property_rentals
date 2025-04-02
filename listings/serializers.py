from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Listing, Booking, ListingView

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class ListingSerializer(serializers.ModelSerializer):
    landlord = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'location', 'price', 'rooms', 'housing_type', 'is_active', 'created_at',
                  'updated_at', 'landlord', 'image']
        read_only_fields = ['owner']


class BookingSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = Booking
        fields = ['id', 'tenant', 'listing', 'start_date', 'end_date', 'status']


class ListingViewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = ListingView
        fields = ['id', 'user', 'listing', 'viewed_at']
