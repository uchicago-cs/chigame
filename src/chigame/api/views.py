# from django.shortcuts import render
from rest_framework import generics

from chigame.api.serializers import GameSerializer
from chigame.games.models import Game

# Create your views here.

# create /games/ endpoint that returns a list of all games


class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


# create /games/<int:pk>/ endpoint that returns a single game
class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
