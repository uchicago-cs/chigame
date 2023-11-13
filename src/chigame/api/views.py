# from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from chigame.api.serializers import GameSerializer, NotificationSerializer, TournamentSerializer, UserSerializer
from chigame.games.models import Game, Notification, Tournament
from chigame.users.models import User, UserProfile

from .permissions import IsUnauthenticated


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUnauthenticated]

    def perform_create(self, serializer):
        user = serializer.save()
        UserProfile.objects.create(user=user, display_name=user.name)


class TournamentCreateView(generics.CreateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAdminUser]


class TournamentListView(generics.ListAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer


class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
