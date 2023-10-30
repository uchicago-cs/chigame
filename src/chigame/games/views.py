from django.views.generic import ListView

from .models import Game, Lobby


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"

class ViewLobbyDetails(ListView):
    model = Lobby
    queryset = Lobby.objects.all()
    template_name = "games/lobby_details.html"
