from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django_tables2 import SingleTableView

from .forms import GameForm
from .models import Game, Lobby, Tournament
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


class GameCreateView(UserPassesTestMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = "games/game_form.html"
    success_url = reverse_lazy("game-list")
    raise_exception = True  # if user is not staff member, raise exception

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


class GameEditView(UserPassesTestMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = "games/game_form.html"
    raise_exception = True  # if user is not staff member, raise exception

    # if edit is successful, redirect to that game's detail page
    def get_success_url(self):
        return reverse_lazy("game-detail", kwargs={"pk": self.kwargs["pk"]})

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


class TournamentListView(ListView):
    model = Tournament
    queryset = Tournament.objects.prefetch_related("matches").all()
    template_name = "tournaments/tournament_list.html"
    context_object_name = "tournament_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Additional context can be added if needed
        return context

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


def search_results(request):
    query = request.GET.get("query")

    """
    The Q object is an object used to encapsulate a collection of keyword
    arguments that can be combined with logical operators (&, |, ~) which
    allows for more advanced searches. More info can be found here at
    https://docs.djangoproject.com/en/4.2/topics/db/queries/#complex-lookups-with-q-objects
    """
    object_list = Game.objects.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    context = {"query_type": "Games", "object_list": object_list}

    return render(request, "pages/search_results.html", context)
