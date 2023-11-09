# from django.shortcuts import render
from rest_framework import generics

from chigame.api.serializers import GameSerializer, UserSerializer
from chigame.games.models import Game
from chigame.users.models import UserProfile


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class UserFriendsAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs["pk"]
        user_profile = UserProfile.objects.get(user_id=user_id)
        return user_profile.friends.all()
