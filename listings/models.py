from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email is required'))
        if not name:
            raise ValueError(_('Name is required'))
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('name'), max_length=30, blank=True)
    role = models.CharField(max_length=50, blank=True, null=True, default='tenant') # added default

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

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


# 5. История просмотров - deleted as was planned as an additional



