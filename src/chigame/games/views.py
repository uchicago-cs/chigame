import xml.etree.ElementTree as ET
from functools import wraps
from random import choice

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .filters import LobbyFilter
from .forms import GameForm, LobbyForm
from .models import Game, Lobby, Match, Player, Tournament
from .tables import LobbyTable


# =============== Games CRUD and Search Views ===============
class GameListView(ListView):
    model = Game
    template_name = "games/game_grid.html"
    paginate_by = 20

    def get_queryset(self):
        """
        Returns a queryset of Game objects sorted and filtered based on the URL parameters.
        https://docs.djangoproject.com/en/4.2/ref/models/querysets/
        """
        queryset = super().get_queryset()
        sort = self.request.GET.get("sort_by", "name-asc")
        players = self.request.GET.get("players", "")
        queryset = apply_sorting_and_filtering(queryset, sort, players)

        return queryset


class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"


class GameCreateView(UserPassesTestMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = "games/game_form.html"
    success_url = reverse_lazy("game-list")  # URL to redirect after successful creation
    raise_exception = True  # if user is not staff member, raise exception

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Game create and edit views share the same template, so this variable lets us know which is which
        # Currently, this is being so that BGG autofilling is only available when creating a game
        context["is_create"] = True

        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Game create and edit views share the same template, so this variable lets us know which is which
        # Currently, this is being so that BGG autofilling is only available when creating a game
        context["is_create"] = False

        return context


# =============== BGG Searching =================
# The following functions involve using the BoardGameGeek API to search for games.
# API documentation: https://boardgamegeek.com/wiki/page/BGG_XML_API2
# ChiGame's documentation: https://github.com/uchicago-cs/chigame/wiki/Games-~-BoardGameGeek-(BGG)-API


def bgg_search_by_name(request):
    """
    Handles a GET request to search for board games by their exact name using the BoardGameGeek (BGG) API.
    Returns a JsonResponse of games with their details.
    """

    if request.method == "GET":
        search_term = request.GET.get("search_term")
        BGG_BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"
        url = f"{BGG_BASE_URL}search?type=boardgame&query={search_term}&exact=1"
        response = requests.get(url)
        # Parse the XML response
        root = ET.fromstring(response.text)

        # Initialize a list to store game data
        games_list = []

        # Iterates over all 'item' elements in the XML tree and retrieves the game details
        # An example XML response can be found here:
        # https://boardgamegeek.com/xmlapi2/search/search?type=boardgame&query=13&exact=1%22
        for game in root.findall(".//item"):
            bgg_id = game.get("id")
            game_data = bgg_get_game_details(bgg_id)
            games_list.append(game_data)

        return JsonResponse({"games_list": games_list})


def bgg_search_by_id(request):
    """
    Handles a GET request to search for a board game by its BoardGameGeek (BGG) ID.
    Returns a JsonResponse of games with their details.
    """
    if request.method == "GET":
        game_id = request.GET.get("game_id")
        game_data = bgg_get_game_details(game_id)
        return JsonResponse({"game_details": game_data})


def bgg_get_game_details(bgg_id):
    """
    Retrieves detailed information about a game from the BoardGameGeek (BGG) API using a given BGG ID.
    The information includes the game's name, image, description, year of publication, player range,
    playtime, suggested age, and complexity rating.

    Args:
    bgg_id (str): The BoardGameGeek ID of the game.

    Returns:
    dict: A dictionary containing various details about the game.
    """
    BGG_BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"

    # Construct the URL to get details of the game with the specified BGG ID
    details_url = f"{BGG_BASE_URL}thing?id={bgg_id}&stats=1"
    details_response = requests.get(details_url)
    # Parse the XML response
    details_root = ET.fromstring(details_response.text)

    # Retrieve the complexity value from the API response, convert it to a float,
    # and round it to two decimal places. If the value is not found, default to None.
    complexity_value = details_root.find(".//averageweight").get("value")
    rounded_complexity = round(float(complexity_value), 2) if complexity_value else None

    # Function to safely get the value from the XML tree
    def get_value(xml_root, tag, attribute="value", default=None):
        element = xml_root.find(f".//{tag}")
        if element is not None:
            return element.get(attribute) if attribute else element.text
        return default

    # Refactored game data structure
    game_data = {
        "BGG_id": bgg_id,
        "name": get_value(details_root, "name"),
        "image": get_value(details_root, "image", attribute=None, default="/static/images/no_picture_available.png"),
        "description": get_value(details_root, "description", attribute=None),
        "year_published": int(get_value(details_root, "yearpublished", default=0)) or None,
        "min_players": get_value(details_root, "minplayers"),
        "max_players": get_value(details_root, "maxplayers"),
        "expected_playtime": get_value(details_root, "playingtime"),
        "min_playtime": get_value(details_root, "minplaytime"),
        "max_playtime": get_value(details_root, "maxplaytime"),
        "suggested_age": get_value(details_root, "minage"),
        "complexity": rounded_complexity,  # The rounded complexity rating of the game
        # Missing fields: category, mechanics
        # No rules field in BGG API
    }

    return game_data


# =============== Lobby Views ===============


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
    if lobby.members.all().count() == lobby.max_players:
        lobby.match_status = 2
    lobby.save()
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


def update_match_status(request, pk):
    # A bit weird: sends Ajax request to change match status when timer runs out.
    lobby = get_object_or_404(Lobby, id=pk)

    if lobby.members.all().count() >= lobby.min_players:
        lobby.match_status = 2
    else:
        lobby.match_status = 3
    lobby.save()

    return JsonResponse({"message": "Match status updated successfully"})


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


def apply_sorting_and_filtering(queryset, sort_param, players_param):
    # Example value of sort_param: "name-asc" or "year_published-desc".
    if sort_param:
        sort_field, sort_direction = sort_param.rsplit("-", 1)
        sort_order = "-" if sort_direction == "desc" else ""

        if sort_field == "name":
            if sort_direction == "desc":
                queryset = queryset.order_by(Lower("name").desc())
            else:
                queryset = queryset.order_by(Lower("name"))
        else:
            queryset = queryset.order_by(f"{sort_order}{sort_field}")

    # Filter by number of players. Handles numeric values and '10+' case.
    if players_param:
        if players_param.isdigit():
            players = int(players_param)
            queryset = queryset.filter(min_players__lte=players, max_players__gte=players)
        elif players_param == "10+":
            queryset = queryset.filter(max_players__gte=10)

    return queryset


def search_results(request):
    query_input = request.GET.get("q")
    sort = request.GET.get("sort_by", "name-asc")
    players = request.GET.get("players", "")
    page_number = request.GET.get("page")

    """
    The Q object is an object used to encapsulate a collection of keyword
    arguments that can be combined with logical operators (&, |, ~) which
    allows for more advanced searches. More info can be found here at
    https://docs.djangoproject.com/en/4.2/topics/db/queries/#complex-lookups-with-q-objects
    """
    object_list = Game.objects.filter(
        Q(name__icontains=query_input)
        | Q(categories__name__icontains=query_input)
        | Q(people__name__icontains=query_input)
        | Q(publishers__name__icontains=query_input)
    ).distinct()  # only show unique game objects (no duplicates)

    object_list = apply_sorting_and_filtering(object_list, sort, players)

    paginator = Paginator(object_list, 20)
    page_obj = paginator.get_page(page_number)

    context = {
        "query_type": "games",
        "object_list": object_list,
        "page_obj": page_obj,
        "current_sort": sort,
        "current_players": players,
        # Any changes to these variables must be reflected in the games_grid.html template
        "query_input": query_input,
    }

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
            else:
                raise Exception("Invalid return value")
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
        self.object.create_tournaments_brackets()  # This should be changed later
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
            game_id=lobby.game.id,
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

    # Checks if everyone has played
    if match.players.all().count() == lobby.members.all().count():
        lobby.match_status = 3
    match.save()
    lobby.save()
    return render(
        request,
        "games/game_coinresult.html",
        {"user_guess": user_guess, "coin_result": coin_result, "correct_guess": correct_guess, "lobby_id": pk},
    )


@login_required
def TournamentChatDetailView(request, pk):
    try:
        tournament = Tournament.objects.get(pk=pk)
        context = {"tournament": tournament}
        if not tournament.chat:
            messages.error(request, "This tournament does not have a chat yet.")
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": pk}))
        return render(request, "tournaments/tournament_chat.html", context)
    except ObjectDoesNotExist:
        messages.error(request, "This tournament does not have a chat yet.")
        return redirect(reverse_lazy("tournament-detail", kwargs={"pk": pk}))
