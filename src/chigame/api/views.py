# from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from chigame.api.filters import GameFilter
from chigame.api.serializers import (
    CategorySerializer,
    GameSerializer,
    LobbySerializer,
    MechanicSerializer,
    UserSerializer,
)
from chigame.games.models import Game, Lobby, User
from chigame.users.models import UserProfile


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (DjangoFilterBackend,)  # Enable DjangoFilterBackend
    filterset_class = GameFilter  # Specify the filter class for this view


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameCategoriesAPIView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        game_id = self.kwargs["pk"]
        game = Game.objects.get(id=game_id)
        return game.categories.all()


class GameMechanicsAPIView(generics.RetrieveAPIView):
    serializer_class = MechanicSerializer

    def get_queryset(self):
        game_id = self.kwargs["pk"]
        game = Game.objects.get(id=game_id)
        return game.mechanics.all()


class UserFriendsAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        user_profile = UserProfile.objects.get(user=user_id)
        return user_profile.friends.all()


class LobbyListView(generics.ListCreateAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer


class LobbyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
