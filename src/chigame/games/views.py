from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import Game, Lobby


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


def search_results(request):
    query = request.GET.get("query")
    object_list = Game.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    context = {"object_list": object_list}

    return render(request, "games/game_list.html", context)
