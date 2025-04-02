from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Listing, ListingView
from .serializers import ListingSerializer, UserSerializer


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.role != 'landlord':
            return Response({'error': 'Only landlords can create listings.'}, status=403)
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        listing = self.get_object()
        if listing.owner != self.request.user:
            return Response({'error': 'You can only edit your own listings.'}, status=403)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            return Response({'error': 'You can only delete your own listings.'}, status=403)
        instance.delete()

    @action(detail=True, methods=['post'])
    def record_view(self, request, pk=None):
        listing = self.get_object()
        if request.user.is_authenticated:
            ListingView.objects.create(user=request.user, listing=listing)
        return Response({'message': 'View recorded'})


class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        form = UserCreationForm(request.data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response(form.errors, status=400)


class LoginViewSet(viewsets.ViewSet):
    def create(self, request):
        form = AuthenticationForm(request, data=request.data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response(form.errors, status=400)


class LogoutViewSet(viewsets.ViewSet):
    def create(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})




