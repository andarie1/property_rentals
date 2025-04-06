from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from listings.views import edit_listing, delete_listing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),  # Все маршруты внутри listings
    path('listings/<int:id>/edit/', edit_listing, name='edit_listing'),
    path('listings/<int:id>/delete/', delete_listing, name='delete_listing'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




