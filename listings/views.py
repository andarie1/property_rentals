from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Listing
from .serializers import ListingSerializer, TenantRegistrationSerializer, LandlordRegistrationSerializer
from django.contrib.auth.forms import AuthenticationForm

# ------------------- REST API -------------------
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

# ------------------- Главная -------------------
def home(request):
    return redirect('listing_list')  # listings/

# ------------------- Регистрация -------------------
def register_choice(request):
    return render(request, 'register_choice.html')

def tenant_register(request):
    if request.method == 'POST':
        serializer = TenantRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect('listing_list')
        else:
            return render(request, 'register_tenant.html', {'form': serializer})
    else:
        form = TenantRegistrationSerializer()
        return render(request, 'register_tenant.html', {'form': form})

def landlord_register(request):
    if request.method == 'POST':
        serializer = LandlordRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect('listing_list')
        else:
            return render(request, 'register_landlord.html', {'form': serializer})
    else:
        form = LandlordRegistrationSerializer()
        return render(request, 'register_landlord.html', {'form': form})

# ------------------- Дашборд арендатора -------------------
@login_required
def tenant_dashboard(request):
    if request.user.role != 'tenant':
        return HttpResponseForbidden("Access denied.")
    return render(request, 'tenant_dashboard.html')

# ------------------- Дашборд арендодателя -------------------
@login_required
def landlord_dashboard(request):
    if request.user.role != 'landlord':
        return HttpResponseForbidden("Access denied.")
    return render(request, 'landlord_dashboard.html')

# ------------------- Логин -------------------
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

# ------------------- Выход -------------------
def logout_view(request):
    logout(request)
    return redirect('home')

# ------------------- Список объявлений -------------------
@login_required
def listing_list(request):
    listings = Listing.objects.all()
    return render(request, 'listings.html', {'listings': listings})

# ------------------- Детали объявления -------------------
@login_required
def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)
    return render(request, 'listing_detail.html', {'listing': listing})

# ------------------- Создать объявление -------------------
@login_required
def create_listing(request):
    if request.user.role != 'landlord':
        return HttpResponseForbidden("Only landlords can create listings.")
    return render(request, 'create_listing.html')

# ------------------- Мой аккаунт -------------------
@login_required
def my_account(request):
    return render(request, 'my_account.html', {
        'user': request.user,
        'role': request.user.role
    })


