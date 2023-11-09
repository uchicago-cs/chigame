# from django.shortcuts import render
from rest_framework import generics

from chigame.api.serializers import GameDetailSerializer, GameListSerializer
from chigame.games.models import Game


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameListSerializer


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameDetailSerializer
