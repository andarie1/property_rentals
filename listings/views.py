from django.shortcuts import render, get_object_or_404, redirect
from .models import Listing, ListingView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout


def home(request):
    if request.method == 'POST':
        return redirect('listing_list')
    return render(request, 'home.html')

def listing_list(request):
    listings = Listing.objects.all()
    return render(request, 'listings.html', {'listings': listings})

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.user.is_authenticated:
        ListingView.objects.create(user=request.user, listing=listing)

    return render(request, 'listings.html', {'listing': listing})

def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def login_register(request):
    return render(request, 'login_register.html')
#_____________________________________________________________
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('')



