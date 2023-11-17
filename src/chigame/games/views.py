from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django_tables2 import SingleTableView

from .forms import GameForm
from .models import Game, Lobby, Tournament
from .tables import LobbyTable
from .tournaments_function import create_tournaments_brackets


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_grid.html"


class LobbyListView(SingleTableView):
    model = Lobby
    table_class = LobbyTable
    template_name = "games/lobby_list.html"


@login_required
def lobby_join(request, pk):
    lobby = get_object_or_404(Lobby, pk=pk)
    joined = Lobby.objects.filter(members=request.user.id)
    print(joined, lobby)
    if lobby in joined:
        messages.error(request, "Already joined.")
        return redirect(reverse("lobby-details", kwargs={"pk": lobby.id}))
    lobby.members.add(request.user)
    return redirect(reverse("lobby-details", kwargs={"pk": lobby.id}))


@login_required
def lobby_leave(request, pk):
    lobby = get_object_or_404(Lobby, pk=pk)
    joined = Lobby.objects.filter(members=request.user.id)
    print(joined, lobby)
    if lobby not in joined:
        messages.error(request, "Haven't joined.")
        return redirect(reverse("lobby-details", kwargs={"pk": lobby.id}))
    lobby.members.remove(request.user)
    return redirect(reverse("lobby-details", kwargs={"pk": lobby.id}))


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


# Tournaments


# Currently, only staff users can create, update, and delete tournaments.
# This may be changed later if we have an official sets of rules for
# tournaments creation, update, and deletion.


# Permission Checkers


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


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


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = "tournaments/tournament_detail.html"
    context_object_name = "tournament"


@method_decorator(staff_required, name="dispatch")
class TournamentCreateView(CreateView):
    model = Tournament
    template_name = "tournaments/tournament_create.html"
    fields = [
        "name",
        "game",
        "start_date",
        "end_date",
        "max_players",
        "description",
        "rules",
        "draw_rules",
        "num_winner",
        "players",
    ]
    # Note: "winner" is not included in the fields because it is not
    # supposed to be set by the user. It will be set automatically
    # when the tournament is over.
    # Note: the "matches" field is not included in the fields because
    # it is not supposed to be set by the user. It will be set automatically
    # by the create tournament brackets mechanism.

    # This method is called when valid form data has been POSTed. It
    # overrides the default behavior of the CreateView class.
    def form_valid(self, form):
        response = super().form_valid(form)
        create_tournaments_brackets(self.object)  # This should be changed later
        # because the brackets should not be created right after the tournament
        # is created. Instead, the brackets should be created when the registration
        # deadline is reached. But for now, we keep it this way for testing.

        # Do something with brackets if needed
        return response

    def get_success_url(self):
        return reverse_lazy("tournament-detail", kwargs={"pk": self.object.pk})


@method_decorator(staff_required, name="dispatch")
class TournamentUpdateView(UpdateView):
    # Note: players should not be allowed to join a tournament after
    # it has started, so it is discouraged (but still allowed) to add
    # new users to "players". However, the new users will not be put
    # into any matches automatically. The staff user will have to
    # manually add them to the matches.
    model = Tournament
    template_name = "tournaments/tournament_update.html"
    fields = [
        "name",
        "game",
        "start_date",
        "end_date",
        "max_players",
        "description",
        "rules",
        "draw_rules",
        "num_winner",
        "matches",
        "players",
    ]
    # Note: "winner" is not included in the fields because it is not
    # supposed to be set by the user. It will be set automatically
    # when the tournament is over.
    # Note: we may remove the "matches" field later for the same reason,
    # but we keep it for now because it is convenient for testing.

    def get_success_url(self):
        return reverse_lazy("tournament-detail", kwargs={"pk": self.object.pk})


@method_decorator(staff_required, name="dispatch")
class TournamentDeleteView(DeleteView):
    model = Tournament
    template_name = "tournaments/tournament_delete.html"
    context_object_name = "tournament"
    success_url = reverse_lazy("tournament-list")


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
