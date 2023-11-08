from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django_tables2 import SingleTableView

from .models import Game, Lobby
from .tables import LobbyTable


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"


class LobbyListView(SingleTableView):
    model = Lobby
    table_class = LobbyTable
    template_name = "games/lobby_list.html"


class ViewLobbyDetails(DetailView):
    model = Lobby
    template_name = "games/lobby_details.html"
    context_object_name = "lobby_detail"


class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"


class GameCreateView(CreateView):
    model = Game
    fields = ["name", "description", "min_players", "max_players"]
    template_name = "games/game_form.html"
    success_url = reverse_lazy("game-list")


class GameEditView(UpdateView):
    model = Game
    fields = ["name", "description", "min_players", "max_players"]
    template_name = "games/game_form.html"

    def get_success_url(self):
        return reverse_lazy("game-detail", kwargs={"pk": self.kwargs["pk"]})
