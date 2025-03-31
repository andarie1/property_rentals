from django.contrib import admin
from django.urls import path
from listings.views import listing_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('listings/', listing_list, name='listing_list'),
]

