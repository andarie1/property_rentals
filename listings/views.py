from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from rest_framework import viewsets
from .models import Listing
from .serializers import ListingSerializer
from rest_framework.permissions import IsAuthenticated

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('/listings')  # Перенаправляем на listings
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_register(request):
    """Обработчик для страницы входа и регистрации"""

    if request.method == 'POST':
        if 'register' in request.POST:  # Пользователь нажал "Зарегистрироваться"
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('home')  # Перенаправляем на главную страницу
        elif 'login' in request.POST:  # Пользователь нажал "Войти"
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('home')

    return render(request, 'auth.html', {'register_form': UserCreationForm(), 'login_form': AuthenticationForm()})

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    return redirect('home')

@login_required
def listing_list(request):
    listings = Listing.objects.all()
    return render(request, 'listings.html', {'listings': listings})

@login_required
def listing_detail(request, id):
    listing = Listing.objects.get(id=id)
    return render(request, 'listing_detail.html', {'listing': listing})

@login_required
def create_listing(request):
    if not hasattr(request.user, 'role') or request.user.role != 'landlord':
        return HttpResponseForbidden("Only landlords can create listings.")
    return render(request, 'create_listing.html')

@login_required
def my_account(request):
    return render(request, 'my_account.html', {'user': request.user})







