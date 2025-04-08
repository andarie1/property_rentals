from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Listing, Review
from .serializers import ListingSerializer
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .forms import TenantRegisterForm, LandlordRegisterForm, ListingForm, ReviewForm, SearchForm

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
            return redirect('listing_list')
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
    listings = Listing.objects.filter(is_active=True).annotate(
        average_rating=Avg('reviews__rating')
    )
    form = SearchForm(request.GET or None)

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        location = form.cleaned_data.get('location')
        min_rooms = form.cleaned_data.get('min_rooms')
        max_rooms = form.cleaned_data.get('max_rooms')
        housing_type = form.cleaned_data.get('housing_type')
        sort_by = form.cleaned_data.get('sort_by')

        if keyword:
            listings = listings.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
        if location:
            listings = listings.filter(location__icontains=location)
        if min_price is not None:
            listings = listings.filter(price__gte=min_price)
        if max_price is not None:
            listings = listings.filter(price__lte=max_price)
        if min_rooms is not None:
            listings = listings.filter(rooms__gte=min_rooms)
        if max_rooms is not None:
            listings = listings.filter(rooms__lte=max_rooms)
        if housing_type:
            listings = listings.filter(housing_type=housing_type)
        if sort_by:
            listings = listings.order_by(sort_by)
        else:
            listings = listings.order_by('-created_at')

    paginator = Paginator(listings, 10)
    page = request.GET.get('page')
    listings = paginator.get_page(page)

    return render(request, 'listings.html', {
        'listings': listings,
        'form': form
    })

# ------------------- Детали объявления -------------------
@login_required
def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)
    reviews = listing.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    user_review = None
    form = None

    if request.user.is_authenticated and request.user.role == 'tenant':
        user_review = Review.objects.filter(tenant=request.user, listing=listing).first()
        if not user_review:
            if request.method == 'POST':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.tenant = request.user
                    review.listing = listing
                    review.save()
                    return redirect('listing_detail', id=listing.id)
            else:
                form = ReviewForm()

    return render(request, 'listing_detail.html', {
        'listing': listing,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form,
        'user_review': user_review
    })

# ------------------- Создать объявление -------------------
@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.landlord = request.user
            listing.save()
            messages.success(request, 'Listing created!')
            return redirect('landlord_dashboard')
    else:
        form = ListingForm()
    return render(request, 'create_listing.html', {'form': form})

@login_required
def edit_listing(request, id):
    listing = get_object_or_404(Listing, id=id, landlord=request.user)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
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

@login_required
def landlord_dashboard(request):
    listings = Listing.objects.filter(landlord=request.user)
    return render(request, 'landlord_dashboard.html', {'listings': listings})

# ----------------- Переключатель ------------------
@login_required
def toggle_listing_status(request, id):
    listing = get_object_or_404(Listing, id=id, landlord=request.user)
    listing.is_active = not listing.is_active
    listing.save()
    return redirect('my_account')

@login_required
def edit_review(request, id):
    review = get_object_or_404(Review, id=id, tenant=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('listing_detail', id=review.listing.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'edit_review.html', {
        'form': form,
        'review': review
    })




