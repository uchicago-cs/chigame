# from django.shortcuts import render
from rest_framework import generics

from chigame.api.serializers import GameSerializer
from chigame.games.models import Game


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
