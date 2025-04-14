from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Listing

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ()}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "role", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "role", "password", "password2"),
        }),
    )
    list_display = ("email", "role", "is_staff")
    search_fields = ("email",)
    ordering = ("email",)

admin.site.register(User, CustomUserAdmin)

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "price", "is_active", "landlord")
    list_filter = ("is_active", "location", "landlord")
    search_fields = ("title", "description", "location")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ["landlord"]


