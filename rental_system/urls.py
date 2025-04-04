from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from listings.views import register, my_account

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    path('listings/', TemplateView.as_view(template_name="listings.html"), name='listings'),
    path('my_account/', my_account, name='my_account'),

    # Исправленный доступ к Login / Register
    path('login/', TemplateView.as_view(template_name="login.html"), name='login'),
    path('register/', register, name='register'),

    path('', include('listings.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




