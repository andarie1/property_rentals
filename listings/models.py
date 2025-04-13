from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        if not password:
            raise ValueError('Password is required')  # Добавьте эту проверку
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    objects = CustomUserManager()


# 2. Объявление
class Listing(models.Model):
    HOUSING_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
    ]

    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings", null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveIntegerField()
    housing_type = models.CharField(max_length=20, choices=HOUSING_TYPES)
    contact_info = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="listing_images/", null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.location} (${self.price})"


# 3. Бронирование
class Booking(models.Model):
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20,
                              choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
                              default='pending')

    def __str__(self):
        return f"Booking {self.id}: {self.tenant} -> {self.listing} ({self.start_date} - {self.end_date})"


# 4. Отзывы
class Review(models.Model):
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id}: {self.listing} by {self.tenant} - {self.rating}★"


# 5. История просмотров
class ListingView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="views")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="views")
    viewed_at = models.DateTimeField(auto_now_add=True)  # Когда смотрел

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"View: {self.user} -> {self.listing} at {self.viewed_at}"



