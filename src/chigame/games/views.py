from django.views.generic import ListView
from django.shortcuts import render, redirect, reverse

from .models import *


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"

def lobby_list(request):
    lobbies = Lobby.objects.all()
    context = {"object_list": lobbies}
    return render(request, "games/lobby_list.html", context)
