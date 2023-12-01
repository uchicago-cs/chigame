from functools import wraps
from random import choice

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .filters import LobbyFilter
from .forms import GameForm, LobbyForm
from .models import Game, Lobby, Match, Player, Tournament
from .tables import LobbyTable


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_grid.html"
    paginate_by = 20


def lobby_list(request):
    queryset = Lobby.objects.all()
    filter = LobbyFilter(request.GET, queryset=queryset)
    table = LobbyTable(filter.qs)

    return render(request, "games/lobby_list.html", {"table": table, "filter": filter})


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


class LobbyCreateView(LoginRequiredMixin, CreateView):
    model = Lobby
    form_class = LobbyForm
    template_name = "games/lobby_form.html"
    success_url = reverse_lazy("lobby-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.lobby_created = timezone.now()
        return super().form_valid(form)


class ViewLobbyDetails(DetailView):
    model = Lobby
    template_name = "games/lobby_details.html"
    context_object_name = "lobby_detail"


class LobbyUpdateView(UpdateView):
    model = Lobby
    form_class = LobbyForm
    template_name = "games/lobby_form.html"

    def get_success_url(self):
        return reverse_lazy("lobby-details", kwargs={"pk": self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        # get the lobby object
        self.object = self.get_object()
        # check if the user making the request is the "host" of the lobby
        if request.user != self.object.created_by and not request.user.is_staff:
            return HttpResponseForbidden("You don't have permission to edit this lobby.")
        return super().dispatch(request, *args, **kwargs)


class LobbyDeleteView(DeleteView):
    model = Lobby
    template_name = "games/lobby_confirm_delete.html"
    success_url = reverse_lazy("lobby-list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.created_by and not request.user.is_staff:
            return HttpResponseForbidden("You don't have permission to delete this lobby.")
        return super().dispatch(request, *args, **kwargs)


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


def search_results(request):
    query = request.GET.get("query")

    """
    The Q object is an object used to encapsulate a collection of keyword
    arguments that can be combined with logical operators (&, |, ~) which
    allows for more advanced searches. More info can be found here at
    https://docs.djangoproject.com/en/4.2/topics/db/queries/#complex-lookups-with-q-objects
    """
    object_list = Game.objects.filter(
        Q(name__icontains=query)
        | Q(categories__name__icontains=query)
        | Q(people__name__icontains=query)
        | Q(publishers__name__icontains=query)
    ).distinct()  # only show unique game objects (no duplicates)
    context = {"query_type": "Games", "object_list": object_list}

    return render(request, "games/game_grid.html", context)


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

    def post(self, request, *args, **kwargs):
        # This method is called when the user clicks the "Join Tournament" or
        # "Withdraw" button
        tournament = Tournament.objects.get(id=request.POST.get("tournament_id"))
        if request.POST.get("action") == "join":
            success = tournament.tournament_sign_up(request.user)
            if success == 0:
                messages.success(request, "You have successfully joined this tournament")
                return redirect(reverse_lazy("tournament-list"))
            elif success == 1:
                messages.error(request, "You have already joined this tournament")
                return redirect(reverse_lazy("tournament-list"))
            elif success == 2:
                messages.error(request, "This tournament is full")
                return redirect(reverse_lazy("tournament-list"))
            elif success == 3:
                messages.error(request, "The registration period for this tournament has ended")
                return redirect(reverse_lazy("tournament-list"))
            else:
                raise Exception("Invalid return value")

        elif request.POST.get("action") == "withdraw":
            success = tournament.tournament_withdraw(request.user)
            if success == 0:
                messages.success(request, "You have successfully withdrawn from this tournament")
                return redirect(reverse_lazy("tournament-list"))
            elif success == 1:
                messages.error(request, "You have not joined this tournament")
                return redirect(reverse_lazy("tournament-list"))
            elif success == 3:
                messages.error(request, "The registration period for this tournament has ended")
                return redirect(reverse_lazy("tournament-list"))
            else:
                raise Exception("Invalid return value")
        else:
            raise ValueError("Invalid action")

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = "tournaments/tournament_detail.html"
    context_object_name = "tournament"

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        tournament = Tournament.objects.get(id=self.kwargs["pk"])
        if tournament.matches.count() == 0 and tournament.status == "registration closed":
            # if the tournament matches have not been created
            tournament.create_tournaments_brackets()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        # This method is called when the user clicks the "Join Tournament" or
        # "Withdraw" button
        tournament = Tournament.objects.get(id=request.POST.get("tournament_id"))
        if request.POST.get("action") == "join":
            success = tournament.tournament_sign_up(request.user)
            if success == 0:
                messages.success(request, "You have successfully joined this tournament")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))
            elif success == 1:
                messages.error(request, "You have already joined this tournament")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))
            elif success == 2:
                messages.error(request, "This tournament is full")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))
            elif success == 3:
                messages.error(request, "The registration period for this tournament has ended")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))
            else:
                raise Exception("Invalid return value")

        elif request.POST.get("action") == "withdraw":
            success = tournament.tournament_withdraw(request.user)
            if success == 0:
                messages.success(request, "You have successfully withdrawn from this tournament")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))
            elif success == 1:
                messages.error(request, "You have not joined this tournament")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))
            elif success == 3:
                messages.error(request, "The registration period for this tournament has ended")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))
            else:
                raise Exception("Invalid return value")

        elif request.POST.get("action") == "join_match":
            pass  # allow players to join their own matches
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        elif request.POST.get("action") == "spectate":
            pass  # allow anyone to spectate
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        else:
            raise ValueError("Invalid action")


@method_decorator(staff_required, name="dispatch")
class TournamentCreateView(CreateView):
    model = Tournament
    template_name = "tournaments/tournament_create.html"
    fields = [
        "name",
        "game",
        "registration_start_date",
        "registration_end_date",
        "tournament_start_date",
        "tournament_end_date",
        "max_players",
        "description",
        "rules",
        "draw_rules",
        "num_winner",
        "players",  # This field should be removed in the production version. For testing only.
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
        "max_players",
        "description",
        "rules",
        "draw_rules",
        "num_winner",
        "matches",
        "players",
    ]
    # Note: the "registration_start_date" and "registration_end_date",
    # "tournament_start_date" and "tournament_end_date" fields are not
    # included because they are not supposed to be updated once the tournament is created.

    # Note: "winner" is not included in the fields because it is not
    # supposed to be set by the user. It will be set automatically
    # when the tournament is over.
    # Note: we may remove the "matches" field later for the same reason,
    # but we keep it for now because it is convenient for testing.

    def form_valid(self, form):
        # Get the current tournament from the database
        current_tournament = get_object_or_404(Tournament, pk=self.kwargs["pk"])

        # Check if the 'players' field has been modified
        form_players = set(form.cleaned_data["players"])
        current_players = set(current_tournament.players.all())
        if len(form_players - current_players) > 0:  # if the players have been added
            raise PermissionDenied("You cannot add new players to the tournament after it has started.")
        elif len(current_players - form_players) > 0:  # if the players have been removed
            removed_players = current_players - form_players  # get the players that have been removed
            for player in removed_players:
                related_match = current_tournament.matches.get(
                    players__in=[player]
                )  # get the match that the player is in
                related_match.players.remove(player)
                if related_match.players.count() == 0:  # if the match is empty, delete it
                    related_match.delete()

        # The super class's form_valid method will save the form data to the database
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tournament-detail", kwargs={"pk": self.object.pk})


@method_decorator(staff_required, name="dispatch")
class TournamentDeleteView(DeleteView):
    model = Tournament
    template_name = "tournaments/tournament_delete.html"
    context_object_name = "tournament"
    success_url = reverse_lazy("tournament-list")


# Placeholder Game
@login_required
def coin_flip_game(request, pk):
    # check if user has already played game
    if Player.objects.filter(user=request.user, match_id__lobby__id=pk).exists():
        return render(request, "games/game_already_played.html")
    return render(request, "games/game_coinflip.html", {"lobby_id": pk})


@login_required
def check_guess(request, pk):
    user_guess = request.POST.get("user_guess")
    coin_result = choice(["heads", "tails"])
    correct_guess = user_guess == coin_result

    lobby = get_object_or_404(Lobby, id=pk)

    # allows two users to play the game
    if Match.objects.filter(lobby__id=pk).exists():
        match = get_object_or_404(Match, lobby__id=pk)
    else:
        # Create Match instance linked to the fetched Lobby
        match = Match.objects.create(
            game_id=1,  # Replace with the actual Game ID
            lobby=lobby,
            date_played=timezone.now()
            # Add other fields as needed
        )

    player = Player.objects.create(
        user=request.user,
        match=match,
    )
    if correct_guess:
        player.outcome = Player.WIN
    else:
        player.outcome = Player.LOSE
    player.save()

    return render(
        request,
        "games/game_coinresult.html",
        {"user_guess": user_guess, "coin_result": coin_result, "correct_guess": correct_guess},
    )


def TournamentChatDetailView(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    context = {"tournament": tournament}
    return render(request, "tournaments/tournament_chat.html", context)
