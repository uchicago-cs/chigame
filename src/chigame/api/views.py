# from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from chigame.api.filters import GameFilter
from chigame.api.serializers import GameSerializer
from chigame.games.models import Game


class GameListView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = (DjangoFilterBackend,)  # Enable DjangoFilterBackend
    filterset_class = GameFilter  # Specify the filter class for this view


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
