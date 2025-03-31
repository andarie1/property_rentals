from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'rooms', 'housing_type', 'is_active', 'created_at')
    list_filter = ('housing_type', 'is_active', 'rooms')
    search_fields = ('title', 'description', 'location')


