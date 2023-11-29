# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from chigame.api.filters import GameFilter
from chigame.api.serializers import GameSerializer, LobbySerializer, MessageSerializer, UserSerializer
from chigame.games.models import Game, Lobby, Message, User
from chigame.users.models import UserProfile


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (DjangoFilterBackend,)  # Enable DjangoFilterBackend
    filterset_class = GameFilter  # Specify the filter class for this view


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class UserFriendsAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        user_profile = get_object_or_404(UserProfile, user=user_id)
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
    lookup_field = "slug"

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)

        # If the lookup_value is an integer, use the id field
        if lookup_value.isdigit():
            return get_object_or_404(User, pk=lookup_value)
        else:
            # Otherwise, use the slug field
            return get_object_or_404(User, username=lookup_value)


class MessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
