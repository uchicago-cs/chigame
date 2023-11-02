from django.shortcuts import render, redirect, reverse
from django.views.generic import DetailView, ListView

from .models import *

class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"

def lobby_list(request):
    lobbies = Lobby.objects.all()
    context = {"object_list": lobbies}
    return render(request, "games/lobby_list.html", context)

class ViewLobbyDetails(DetailView):	
    model = Lobby	
    template_name = "games/lobby_details.html"
    context_object_name = "lobby_detail"

class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"
