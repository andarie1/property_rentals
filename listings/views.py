from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
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
    return render(request, 'home.html')

# ------------------- Регистрация -------------------
def register_choice(request):
    return render(request, 'register_choice.html')


def tenant_register(request):
    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('listing_list')
    else:
        form = TenantRegisterForm()
    return render(request, 'register_tenant.html', {'form': form})


from .forms import TenantRegisterForm, LandlordRegisterForm, ListingForm


def landlord_register(request):
    if request.method == 'POST':
        form = LandlordRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('listing_list')
    else:
        form = TenantRegisterForm()
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
    listings = Listing.objects.filter(is_active=True).order_by('-created_at')
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

@login_required
def edit_listing(request, id):
    listing = get_object_or_404(Listing, id=id, landlord=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('my_account')
    else:
        form = ListingForm(instance=listing)
    return render(request, 'edit_listing.html', {'form': form, 'listing': listing})

@login_required
def delete_listing(request, id):
    listing = get_object_or_404(Listing, id=id, landlord=request.user)
    if request.method == 'POST':
        listing.delete()
        return redirect('my_account')
    return render(request, 'delete_listing.html', {'listing': listing})

# ------------------- Мой аккаунт -------------------
@login_required
def my_account(request):
    if request.user.role == 'tenant':
        return redirect('tenant_dashboard')
    elif request.user.role == 'landlord':
        return redirect('landlord_dashboard')
    return HttpResponseForbidden("Access denied.")
# ----------------- Переключатель ------------------
@login_required
def toggle_listing_status(request, id):
    listing = get_object_or_404(Listing, id=id, landlord=request.user)
    listing.is_active = not listing.is_active
    listing.save()
    return redirect('my_account')

