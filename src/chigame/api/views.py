# from django.shortcuts import render
from api.serializers import GameSerializer
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

from src.chigame.games.models import Game

# Create your views here.

# create /games/ endpoint that returns a list of all games


class GameListView(ListAPIView):
    model = Game
    serializer_class = GameSerializer


# create /games/<int:pk>/ endpoint that returns a single game
class GameDetailView(RetrieveUpdateDestroyAPIView):
    model = Game
    serializer_class = GameSerializer
