from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listings/', views.listing_list, name='listing_list'),
    path('listings/<int:id>/', views.listing_detail, name='listing_detail'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('login_register/', views.login_register, name='login_register'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
