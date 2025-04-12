from django import forms
from .models import Listing, Review, Booking
from django.contrib.auth import get_user_model


User = get_user_model()

class TenantRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = "tenant"
        if commit:
            user.save()
        return user


class LandlordRegisterForm(TenantRegisterForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "landlord"
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

STATUS_CHOICES = (
    (True, 'Active'),
    (False, 'Inactive'),
)

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'location', 'price', 'rooms', 'housing_type', 'is_active', 'image', 'contact_info']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].initial = True


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i}★') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Leave your comment...'}),
        }

class SearchForm(forms.Form):
    keyword = forms.CharField(required=False)
    min_price = forms.IntegerField(required=False, min_value=0)
    max_price = forms.IntegerField(required=False, min_value=0)
    location = forms.CharField(required=False)
    min_rooms = forms.IntegerField(required=False, min_value=0)
    max_rooms = forms.IntegerField(required=False, min_value=0)
    housing_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Any')] + list(Listing.HOUSING_TYPES)
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('price', 'Price (Low to High)'),
            ('-price', 'Price (High to Low)'),
            ('created_at', 'Date (Oldest First)'),
            ('-created_at', 'Date (Newest First)'),
        ]
    )

import datetime

class BookingForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.date.today() + datetime.timedelta(days=1))
    end_date = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date < datetime.date.today() + datetime.timedelta(days=1):
                self.add_error('start_date', "Start date must be at least tomorrow.")
            if end_date <= start_date:
                self.add_error('end_date', "End date must be after start date.")
        return cleaned_data

