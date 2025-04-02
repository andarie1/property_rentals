from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tenant')

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="listings_users_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="listings_users_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


# 2. Объявление
class Listing(models.Model):
    HOUSING_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
    ]

    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveIntegerField()
    housing_type = models.CharField(max_length=20, choices=HOUSING_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="listing_images/", null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.location} (${self.price})"


# 3. Бронирование
class Booking(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
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
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id}: {self.listing} by {self.tenant} - {self.rating}★"


# 5. История просмотров
class ListingView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="views")  # Кто смотрел
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="views")  # Что смотрел
    viewed_at = models.DateTimeField(auto_now_add=True)  # Когда смотрел

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"View: {self.user} -> {self.listing} at {self.viewed_at}"









