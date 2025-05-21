import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from functools import wraps
from random import choice

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Avg, Case, Count, ExpressionWrapper, F, FloatField, Q, Value, When
from django.db.models.functions import Lower
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from django.views.generic.edit import FormMixin
from rest_framework import status

# ============ new imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chigame.users.models import User

from .filters import LobbyFilter
from .forms import GameForm, IFGameForm, LobbyForm, ReviewForm
from .models import (
    Chat,
    Checkers,
    CheckersBoard,
    CheckersTurn,
    Feedback,
    Game,
    GameList,
    InteractiveFictionGame,
    Lobby,
    Match,
    Player,
    Review,
    Tournament,
)
from .simulation_utils import (
    MultiStageSimulator,
    RoundRobinSimulator,
    TournamentSimulator,
    run_complete_tournament_simulation,
)
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
        # Adding average rating and popularity to the queryset
        queryset = (
            super()
            .get_queryset()
            .annotate(avg_rating=Avg("reviews__rating"), popularity=Count("reviews__is_public"))
            .annotate(rating_percentage=ExpressionWrapper((F("avg_rating") / 5) * 100, output_field=FloatField()))
        )
        sort = self.request.GET.get("sort_by", "name-asc")
        players = self.request.GET.get("players", "")
        queryset = apply_sorting_and_filtering(queryset, sort, players)

        return queryset


class GameDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"
    form_class = ReviewForm

    # for twine files, redirect to different IF view
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("game-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["reviews"] = Review.objects.filter(game=self.object)
        context["popularity"] = self.object.reviews.count()
        context["avg_rating"] = self.object.reviews.filter(is_public=True).aggregate(Avg("rating"))["rating__avg"]

        # FOR IF/twine GAMES
        context["is_twine_game"] = self.object.twine_file.name.endswith(".html") if self.object.twine_file else False
        context["recommended_games"] = get_recommended_games(
            game=self.object,
            user=self.request.user if self.request.user.is_authenticated else None,
            limit=4,  # this is to show 4 reccomendations
        )
        # Include the user's GameLists: default Favorites plus others
        if self.request.user.is_authenticated:
            favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=self.request.user)
            context["favorites_list"] = favorites_list
            context["game_lists"] = GameList.objects.filter(created_by=self.request.user).exclude(pk=favorites_list.pk)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.game = self.object
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class GameCreateView(UserPassesTestMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = "games/game_form.html"
    raise_exception = True  # if user is not staff member, raise exception

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context

    # Ensure the uploaded Twine .html file is saved to the Game model
    def form_valid(self, form):
        self.object = form.save(commit=False)
        # ✅ Manually assign uploaded file
        if self.request.FILES.get("twine_file"):
            self.object.twine_file = self.request.FILES["twine_file"]
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        if self.object.twine_file and self.object.twine_file.name.endswith(".html"):
            return reverse("interactive-fiction-detail", kwargs={"pk": self.object.pk})
        return reverse("game-detail", kwargs={"pk": self.object.pk})


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
        context["is_create"] = False
        return context

# ===========For storing twine in database ============== 

def serve_twine_from_db(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if not game.twine_file_content:
        raise Http404("No Twine file stored in database.")
    return HttpResponse(
        game.twine_file_content,
        content_type="text/html",
        headers={"Content-Disposition": f'inline; filename="{game.twine_file_name}"'},
    )

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


def get_recommended_games(game, user=None, limit=5):
    """
    Returns a queryset of recommended games based on multiple weighted factors.

    Args:
        game: The reference Game object
        user: Optional User object to check play history
        limit: Maximum number of games to return

    Returns:
        QuerySet of Game objects ordered by recommendation score
    """

    # Settled on a recommendation system that combines multiple factors
    # (as opposed to having it only be category based):
    # Game categories (40% weight)
    # Game mechanics (30% weight)
    # Game designers/artists (15% weight)
    # Similar complexity ratings (10% weight)
    # Similar playtime (5% weight)
    #
    # The reason I went with this weighted approach is to provide more well
    # rounded recommendations than
    # using categories alone. Also, I deprioritized, but didn't exclude, games
    # the user has already played.

    all_games = Game.objects.exclude(id=game.id)

    game_categories = game.categories.all()
    game_mechanics = game.mechanics.all()
    game_people = game.people.all()

    all_games = all_games.annotate(category_score=Count("categories", filter=Q(categories__in=game_categories)) * 0.4)

    all_games = all_games.annotate(mechanics_score=Count("mechanics", filter=Q(mechanics__in=game_mechanics)) * 0.3)

    all_games = all_games.annotate(people_score=Count("people", filter=Q(people__in=game_people)) * 0.15)

    if game.complexity:
        # Convert Decimal to float before arithmetic operations
        complexity_value = float(game.complexity)
        all_games = all_games.annotate(
            complexity_score=Case(
                When(complexity__range=(complexity_value - 0.5, complexity_value + 0.5), then=0.1),
                When(complexity__range=(complexity_value - 1.0, complexity_value + 1.0), then=0.05),
                default=Value(0),
                output_field=FloatField(),
            )
        )
    else:
        all_games = all_games.annotate(complexity_score=Value(0, output_field=FloatField()))
    if game.expected_playtime:
        # Convert to float before arithmetic
        playtime_value = float(game.expected_playtime)
        all_games = all_games.annotate(
            playtime_score=Case(
                When(expected_playtime__range=(playtime_value * 0.8, playtime_value * 1.2), then=0.05),
                default=Value(0),
                output_field=FloatField(),
            )
        )
    else:
        all_games = all_games.annotate(playtime_score=Value(0, output_field=FloatField()))
    if user and user.is_authenticated:
        played_game_ids = Match.objects.filter(players=user).values_list("game_id", flat=True)
        all_games = all_games.annotate(
            played_penalty=Case(When(id__in=played_game_ids, then=0.2), default=1.0, output_field=FloatField())
        )
    else:
        all_games = all_games.annotate(played_penalty=Value(1.0, output_field=FloatField()))

    all_games = all_games.annotate(
        total_score=(
            F("category_score")
            + F("mechanics_score")
            + F("people_score")
            + F("complexity_score")
            + F("playtime_score")
        )
        * F("played_penalty")
    ).order_by("-total_score")

    return all_games[:limit]


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


# =============== Interactive Fiction Views ===============
class InteractiveFictionView(TemplateView):
    template_name = "games/interactive-fiction/IF_game_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest_game = Game.objects.filter(twine_file__isnull=False).order_by("-id").first()

        if not latest_game:
            # fallback dummy game to prevent pk=None
            latest_game = Game.objects.create(
                name="Untitled IF Game",
                description="Temporary IF placeholder",
                min_players=1,
                max_players=1,
                complexity=1.0,
            )

        context["game"] = latest_game

        if latest_game.twine_file:
            context["uploaded_file_url"] = latest_game.twine_file.url

        return context


class IFGameCreateView(UserPassesTestMixin, CreateView):
    model = InteractiveFictionGame
    form_class = IFGameForm
    template_name = "games/interactive-fiction/IF_game_create.html"
    success_url = reverse_lazy("game-list")

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UploadFileView(View):
    def post(self, request, pk=None):
        uploaded_file = request.FILES.get("uploaded_file")

        if uploaded_file:
            # Save the file to twine_games/
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "twine_games"))
            safe_filename = uploaded_file.name.replace(" ", "_")
            filename = fs.save(safe_filename, uploaded_file)

            # Create a basic Game instance
            game = Game.objects.create(
                name=uploaded_file.name.replace(".html", ""),
                description="Uploaded Twine game",
                min_players=1,
                max_players=1,
                complexity=1,
                twine_file=f"twine_games/{filename}",
            )

            messages.success(request, f"Game '{game.name}' uploaded successfully!")
            return redirect("game-detail", pk=game.pk)

        messages.error(request, "No file selected.")
        return redirect("interactive-fiction")


# =============== Tournaments Views ===============


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
    template_name = "tournaments/tournament_list.html"
    context_object_name = "tournament_list"

    def get_queryset(self):
        # If the user is staff, show all tournaments
        if self.request.user.is_staff:
            return Tournament.objects.prefetch_related("matches").all()

        # For non-staff users, show only tournaments they are part of
        return Tournament.objects.prefetch_related("matches").filter(players=self.request.user)

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        for tournament in self.object_list:
            tournament.check_and_end_tournament()  # check if the tournament has ended
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        # This method is called when the user clicks the "Join Tournament" or
        # "Withdraw" button
        if request.POST.get("tournament_id") == "":  # switch view
            pass
        else:
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

        elif request.POST.get("action") == "archive":
            tournament.set_archive(True)
            messages.success(request, "You have successfully archived this tournament")
            return redirect(reverse_lazy("tournament-list"))

        elif request.POST.get("action") == "unarchive":
            tournament.set_archive(False)
            messages.success(request, "You have successfully unarchived this tournament")
            return redirect(reverse_lazy("tournament-list"))

        elif request.POST.get("action") == "switch_archive":
            return redirect(reverse_lazy("tournament-archived"))

        else:
            raise ValueError("Invalid action")

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = "tournaments/tournament_detail.html"
    context_object_name = "tournament"

    def get_simulation_type(self, request, tournament_id):
        if request.session.get(f"tournament_{tournament_id}_round_robin_mode", False):
            return "round_robin"
        elif request.session.get(f"tournament_{tournament_id}_multi_stage_mode", False):
            return "multi_stage"
        elif request.session.get(f"tournament_{tournament_id}_double_elimination", False):
            return "double"
        else:
            return "single"

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        tournament = Tournament.objects.get(id=self.kwargs["pk"])
        self.object = self.get_object()

        if not request.user.is_staff and request.user not in tournament.players.all():
            messages.error(request, "You are not authorized to view this tournament.")
            return redirect("tournament-list")

        if tournament.matches.count() == 0 and tournament.status in ["registration closed", "tournament in progress"]:
            tournament.create_tournaments_brackets()
        tournament.check_and_end_tournament()

        simulation_mode = request.session.get(f"tournament_{tournament.id}_simulation_mode", False)
        simulation_type = self.get_simulation_type(request, tournament.id)
        context = self.get_context_data()
        context["simulation_mode"] = simulation_mode
        context["simulation_type"] = simulation_type

        if simulation_mode:
            simulator_data = request.session.get(f"tournament_{tournament.id}_simulator_data", None)
            if not simulator_data:
                if simulation_type == "single":
                    simulator = TournamentSimulator(tournament)
                    simulator.set_tournament_type(False)
                    simulator.initialize_simulation()
                    simulator_data = simulator.get_bracket_data()

                elif simulation_type == "double":
                    simulator = TournamentSimulator(tournament)
                    simulator.set_tournament_type(True)
                    simulator.initialize_simulation()
                    simulator_data = simulator.get_bracket_data()

                elif simulation_type == "round_robin":
                    simulator = RoundRobinSimulator(list(tournament.players.all()))
                    simulator.simulate_all_matches()
                    simulator_data = simulator.get_bracket_data()

                elif simulation_type == "multi_stage":
                    simulator = MultiStageSimulator(list(tournament.players.all()))
                    simulator_data = simulator.get_bracket_data()

                request.session[f"tournament_{tournament.id}_simulator_data"] = simulator_data
                request.session.modified = True

            context["simulation_data"] = simulator_data

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        tournament = Tournament.objects.get(id=request.POST.get("tournament_id"))
        simulation_type = self.get_simulation_type(request, tournament.id)
        action = request.POST.get("action")

        if action == "toggle_simulation_mode":
            current_mode = request.session.get(f"tournament_{tournament.id}_simulation_mode", False)
            request.session[f"tournament_{tournament.id}_simulation_mode"] = not current_mode

            if f"tournament_{tournament.id}_simulator_data" in request.session:
                del request.session[f"tournament_{tournament.id}_simulator_data"]

            messages.success(request, f"Simulation mode {'deactivated' if current_mode else 'activated'}")
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        elif action == "set_tournament_type":
            tournament_type = request.POST.get("tournament_type")
            is_double_elimination = tournament_type == "double"

            request.session[f"tournament_{tournament.id}_double_elimination"] = is_double_elimination
            request.session[f"tournament_{tournament.id}_round_robin_mode"] = tournament_type == "round_robin"
            request.session[f"tournament_{tournament.id}_multi_stage_mode"] = tournament_type == "multi_stage"

            if f"tournament_{tournament.id}_simulator_data" in request.session:
                del request.session[f"tournament_{tournament.id}_simulator_data"]

            request.session.modified = True

            messages.success(request, f"Tournament type set to {tournament_type.replace('_', ' ').title()}")
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        # round robin simulation
        elif simulation_type == "round_robin":
            if request.POST.get("action") == "start_simulation":
                simulator = RoundRobinSimulator(list(tournament.players.all()))
                simulator.simulate_all_matches()
                simulation_data = simulator.get_bracket_data()
                request.session[f"tournament_{tournament.id}_simulator_data"] = simulation_data
                request.session.modified = True

                messages.success(request, "Round Robin simulation started!")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            elif request.POST.get("action") == "re-run_simulation":
                if f"tournament_{tournament.id}_simulator_data" in request.session:
                    del request.session[f"tournament_{tournament.id}_simulator_data"]

                messages.success(request, "Simulation reset")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        # multi-stage simulation
        elif simulation_type == "multi_stage":
            if action == "simulate_round_robin_phase":
                simulator = MultiStageSimulator(list(tournament.players.all()))
                simulator.simulate_round_robin_only()
                request.session[f"tournament_{tournament.id}_simulator_data"] = simulator.get_bracket_data()
                request.session.modified = True

                messages.success(request, "Round Robin Phase simulated!")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            elif action == "simulate_knockout_phase":
                simulator_data = request.session.get(f"tournament_{tournament.id}_simulator_data")
                if not simulator_data or not simulator_data.get("round_robin_complete"):
                    messages.error(request, "Please complete the Round Robin Phase first.")
                    return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

                simulator = MultiStageSimulator(list(tournament.players.all()))
                simulator.round_robin_simulated = True
                simulator.results = {}
                for match in simulator_data["round_robin_matches"]:
                    if match["winner"]:
                        p1_id = match["players"][0]["id"]
                        p2_id = match["players"][1]["id"]
                        winner_id = match["winner"]
                        simulator.results[(p1_id, p2_id)] = winner_id

                simulator.simulate_knockout_only()

                request.session[f"tournament_{tournament.id}_simulator_data"] = simulator.get_bracket_data()
                request.session.modified = True

                messages.success(request, "Knockout Phase simulated!")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            elif action == "run_full_simulation":
                simulator = MultiStageSimulator(list(tournament.players.all()))
                simulator.simulate_tournament()

                request.session[f"tournament_{tournament.id}_simulator_data"] = simulator.get_bracket_data()
                request.session.modified = True

                messages.success(request, "Full tournament simulation completed!")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        # single and double elimination simulation
        elif simulation_type == "single" or simulation_type == "double":
            if request.POST.get("action") == "simulate_match":
                # Simulate a specific match
                match_id = request.POST.get("match_id")

                # Get the simulator data from the session
                simulator_data = request.session.get(f"tournament_{tournament.id}_simulator_data", None)
                if not simulator_data:
                    messages.error(request, "Simulation data not found. Please restart the simulation.")
                    return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

                # Create a simulator instance and load the data
                simulator = TournamentSimulator(tournament)
                simulator.set_tournament_type(
                    request.session.get(f"tournament_{tournament.id}_double_elimination", False)
                )
                simulator.initialize_simulation()

                # Update the simulator with the current state
                simulator.simulated_matches = {}
                for round_num, brackets in simulator_data["rounds"].items():
                    for bracket_type, matches in brackets.items():
                        for match in matches:
                            # Ensure match ID is a string
                            match_id_in_data = str(match["id"])
                            match_data = {
                                "match": None,
                                "players": [
                                    user
                                    for user in tournament.players.all()
                                    if user.id in [p["id"] for p in match["players"]]
                                ],
                                "winner": next(
                                    (user for user in tournament.players.all() if user.id == match["winner"]), None
                                ),
                                "loser": next(
                                    (user for user in tournament.players.all() if user.id == match["loser"]), None
                                ),
                                "round": int(round_num),
                                "bracket": bracket_type,
                            }
                            simulator.simulated_matches[match_id_in_data] = match_data

                simulator.current_round = simulator_data["current_round"]

                # Simulate the match
                if match_id not in simulator.simulated_matches:
                    messages.error(request, f"Match ID {match_id} not found in simulation data")
                    return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

                winner, loser = simulator.simulate_match_outcome(match_id)

                # Save the updated simulator data
                updated_data = simulator.get_bracket_data()
                request.session[f"tournament_{tournament.id}_simulator_data"] = updated_data
                request.session.modified = True

                if winner:
                    messages.success(request, f"Match simulated successfully. Winner: {winner.username}")
                else:
                    messages.error(request, "Failed to simulate match. No winner determined.")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            elif request.POST.get("action") == "advance_round":
                # Advance to the next round
                simulator_data = request.session.get(f"tournament_{tournament.id}_simulator_data", None)
                if not simulator_data:
                    messages.error(request, "Simulation data not found. Please restart the simulation.")
                    return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

                # Create a simulator instance and load the data
                simulator = TournamentSimulator(tournament)
                simulator.set_tournament_type(
                    request.session.get(f"tournament_{tournament.id}_double_elimination", False)
                )

                # Update the simulator with the current state
                simulator.simulated_matches = {}
                for round_num, brackets in simulator_data["rounds"].items():
                    for bracket_type, matches in brackets.items():
                        for match in matches:
                            match_data = {
                                "match": None,
                                "players": [
                                    user
                                    for user in tournament.players.all()
                                    if user.id in [p["id"] for p in match["players"]]
                                ],
                                "winner": next(
                                    (user for user in tournament.players.all() if user.id == match["winner"]), None
                                ),
                                "loser": next(
                                    (user for user in tournament.players.all() if user.id == match["loser"]), None
                                ),
                                "round": int(round_num),
                                "bracket": bracket_type,
                            }
                            simulator.simulated_matches[str(match["id"])] = match_data

                simulator.current_round = simulator_data["current_round"]

                # Check if all matches in the current round have winners
                current_round_matches = [
                    m for m in simulator.simulated_matches.values() if m["round"] == simulator.current_round
                ]

                all_matches_have_winners = all(m["winner"] is not None for m in current_round_matches)

                if not all_matches_have_winners:
                    messages.error(
                        request, "Cannot advance to next round until all matches in the current round have winners."
                    )
                    return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

                # Create next round matches
                next_round_matches = simulator.create_next_round_matches()

                if not next_round_matches:
                    messages.info(request, "Tournament has reached its conclusion. No more rounds to advance to.")
                    return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

                # For double elimination, check if we need to create the final match
                if simulator.is_double_elimination:
                    # Check if we've reached the final match condition
                    winners_bracket = [m for m in simulator.simulated_matches.values() if m["bracket"] == "winners"]
                    losers_bracket = [m for m in simulator.simulated_matches.values() if m["bracket"] == "losers"]

                    if (len(winners_bracket) > 0 and all(m["winner"] for m in winners_bracket)) and (
                        len(losers_bracket) > 0 and all(m["winner"] for m in losers_bracket)
                    ):
                        # Create the final match
                        simulator.create_final_match()

                # Save the updated simulator data
                updated_data = simulator.get_bracket_data()
                request.session[f"tournament_{tournament.id}_simulator_data"] = updated_data
                request.session.modified = True

                messages.success(request, f"Advanced to round {simulator.current_round}")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            elif request.POST.get("action") == "reset_simulation":
                # Reset the simulation
                if f"tournament_{tournament.id}_simulator_data" in request.session:
                    del request.session[f"tournament_{tournament.id}_simulator_data"]

                messages.success(request, "Simulation reset")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            elif request.POST.get("action") == "run_full_simulation":
                # Run a complete simulation
                is_double_elimination = request.session.get(f"tournament_{tournament.id}_double_elimination", False)
                simulation_data = run_complete_tournament_simulation(tournament, is_double_elimination)
                request.session[f"tournament_{tournament.id}_simulator_data"] = simulation_data

                messages.success(request, "Full tournament simulation completed")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        elif request.POST.get("action") == "join":
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
            # Get the user's current match in the tournament
            user_matches = tournament.matches.filter(players=request.user)
            if not user_matches.exists():
                messages.error(request, "You don't have any matches in this tournament.")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            # Get the first match (there should only be one active match per player)
            match = user_matches.first()

            # Check if the match is already in progress
            if match.lobby.match_status == Lobby.Viewable:
                messages.error(request, "This match is already in progress.")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            # Check if the match is already finished
            if match.lobby.match_status == Lobby.Finished:
                messages.error(request, "This match has already finished.")
                return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

            # Add user to lobby members if not already there
            if request.user not in match.lobby.members.all():
                match.lobby.members.add(request.user)
                match.lobby.save()
                messages.success(request, "You have joined the match lobby.")

            # Check if all players are ready
            if match.players.count() == match.lobby.members.count():
                # Start the match
                match.lobby.match_status = Lobby.Viewable
                match.lobby.save()
                messages.success(request, "Match has started!")
            else:
                messages.info(
                    request,
                    f"Waiting for other players to join... ({match.lobby.members.count()}/{match.players.count()})",
                )

            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        elif request.POST.get("action") == "spectate":
            pass  # allow anyone to spectate
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        elif request.POST.get("action") == "archive":
            tournament.set_archive(True)
            messages.success(request, "You have successfully archived this tournament")
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        elif request.POST.get("action") == "unarchive":
            tournament.set_archive(False)
            messages.success(request, "You have successfully unarchived this tournament")
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": tournament.pk}))

        else:
            raise ValueError("Invalid action")


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

    def form_valid(self, form):
        user = self.request.user

        if form.cleaned_data["players"].count() > form.cleaned_data["max_players"]:
            messages.error(self.request, "The number of players cannot exceed the maximum number of players")
            return redirect(reverse_lazy("tournament-create"))

        # Check if the user is not a staff member and has less than one token
        if not user.is_staff and user.tokens < 1:
            messages.error(self.request, "You do not have enough tokens to create a tournament.")
            return redirect("tournament-list")

        # If the user is not staff, deduct a token
        if not user.is_staff:
            user.tokens -= 1
            user.save()

        # Save the form instance but don't commit to the database yet
        tournament = form.save(commit=False)
        tournament.created_by = user
        tournament.save()

        players = form.cleaned_data["players"]
        tournament.players.add(*players)

        # Auto-create a chat for this respective tournament
        chat = Chat(tournament=tournament)
        chat.save()

        # (Optional) Insert bracket-related logic here if needed

        # Redirect to the tournament's detail page or another appropriate response
        self.object = tournament
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("tournament-detail", kwargs={"pk": self.object.pk})


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
        "players",
    ]

    def dispatch(self, request, *args, **kwargs):
        # Get the tournament object
        tournament = self.get_object()

        # Check if the current user is the creator of the tournament
        if tournament.created_by != request.user and not request.user.is_staff:
            messages.error(self.request, "You do not have permission to edit this tournament.")
            return redirect("tournament-list", pk=self.kwargs["pk"])

        # Continue with the normal flow
        return super().dispatch(request, *args, **kwargs)

    # Note: the "registration_start_date" and "registration_end_date",
    # "tournament_start_date" and "tournament_end_date" fields are not
    # included because they are not supposed to be updated once the tournament is created.

    # Note: "winner" is not included in the fields because it is not
    # supposed to be set by the user. It will be set automatically
    # when the tournament is over.
    # Note: we may remove the "matches" field later for the same reason,
    # but we keep it for now because it is convenient for testing.

    def form_valid(self, form):
        current_tournament = get_object_or_404(Tournament, pk=self.kwargs["pk"])
        # Determine if the user is staff or the creator of the tournament
        is_staff = self.request.user.is_staff

        # Check if the 'players' field has been modified
        form_players = set(form.cleaned_data["players"])
        current_players = set(current_tournament.players.all())

        # Prevent non-staff from modifying 'players' if there are changes
        if form_players != current_players and not is_staff:
            messages.error(self.request, "You do not have permission to modify players.")
            return redirect("tournament-detail", pk=self.kwargs["pk"])

        # Get the set of players before and after the form submission
        # the tournament cannot be updated if it has ended
        if current_tournament.status == "tournament ended":
            messages.error(self.request, "You cannot update a tournament that has ended.")
            return redirect(reverse_lazy("tournament-detail", kwargs={"pk": self.kwargs["pk"]}))

        # Check if new players are being added
        new_players = form_players - current_players
        if new_players:
            # Allow only staff to add new players if the tournament has started
            if now() >= current_tournament.tournament_start_date and not is_staff:
                messages.error(self.request, "You cannot add new players to the tournament after it has started.")
                return redirect("tournament-detail", pk=self.kwargs["pk"])

        # Handle player removal
        if len(current_players - form_players) > 0:  # Players have been removed
            removed_players = current_players - form_players
            for player in removed_players:
                # Handle multiple matches for a player
                related_matches = current_tournament.matches.filter(players__in=[player])
                for match in related_matches:
                    match.players.remove(player)
                    if match.players.count() == 0:  # if the match is empty, delete it
                        match.delete()

        # Check for exceeding maximum number of players
        if form.cleaned_data["players"].count() > form.cleaned_data["max_players"]:
            messages.error(self.request, "The number of players cannot exceed the maximum number of players")
            return redirect(reverse_lazy("tournament-update", kwargs={"pk": self.kwargs["pk"]}))

        # Save the form data to the database using the superclass's method
        # This allows updating of other fields by the creator or staff, regardless of the tournament's status
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("tournament-detail", kwargs={"pk": self.object.pk})


def distribute_tokens():
    # Placeholder for future date check
    # thirty_days_ago = datetime.now() - timedelta(days=30)
    # users = User.objects.filter(tokens__lt=3, last_token_distribution__lt=thirty_days_ago)

    users = User.objects.filter(tokens__lt=3)
    for user in users:
        # Add future logic for updating last_token_distribution
        # user.last_token_distribution = datetime.now()
        user.tokens += 1
        user.save()


@method_decorator(staff_required, name="dispatch")
class TournamentDeleteView(DeleteView):
    model = Tournament
    template_name = "tournaments/tournament_delete.html"
    context_object_name = "tournament"
    success_url = reverse_lazy("tournament-list")


class TournamentArchivedListView(ListView):
    model = Tournament
    queryset = Tournament.objects.prefetch_related("matches").all()
    template_name = "tournaments/tournament_archived_list.html"
    context_object_name = "tournament_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tournament_list"] = self.get_all_archived()
        return context

    def get_all_archived(self):
        return self.get_queryset().filter(archived=True)

    def post(self, request, *args, **kwargs):
        # This method is called when the user clicks the "Join Tournament" or
        # "Withdraw" button
        if request.POST.get("tournament_id") == "":  # switch view
            pass
        else:
            tournament = Tournament.objects.get(id=request.POST.get("tournament_id"))

        if request.POST.get("action") == "archive":
            tournament.set_archive(True)
            messages.success(request, "You have successfully archived this tournament")
            return redirect(reverse_lazy("tournament-archived"))

        elif request.POST.get("action") == "unarchive":
            tournament.set_archive(False)
            messages.success(request, "You have successfully unarchived this tournament")
            return redirect(reverse_lazy("tournament-archived"))

        elif request.POST.get("action") == "switch_all":
            return redirect(reverse_lazy("tournament-list"))

        else:
            raise ValueError("Invalid action")

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


# Tournament Feedback Views
@login_required
def tournament_feedback_list(request, tournament_id):
    """
    View to display all feedback for a specific tournament.
    Only the owner of the tournament can access this view.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Check if the requesting user is the owner of the tournament
    if tournament.created_by != request.user:
        # Redirect or show an error message if the user is not the owner
        messages.error(request, "You are not authorized to view feedback for this tournament.")
        return redirect("tournament-list")  # Redirect to the tournament list or another appropriate page

    # Retrieve feedback for the tournament
    feedback_list = Feedback.objects.filter(tournament=tournament).order_by("-created_at")
    return render(
        request,
        "tournaments/tournament_feedback_list.html",
        {"tournament": tournament, "feedback_list": feedback_list},
    )


@login_required
def user_feedback_list(request):
    """
    View to display all feedback submitted by the logged-in user.
    """
    user_feedback = Feedback.objects.filter(user=request.user).order_by("-created_at")

    # Get the first tournament associated with the user's feedback (if any)
    tournament = user_feedback.first().tournament if user_feedback.exists() else None

    return render(
        request,
        "tournaments/tournament_user_feedback.html",
        {"user_feedback": user_feedback, "tournament": tournament},
    )


@login_required
def submit_feedback(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if request.method == "POST":
        comment = request.POST.get("content")  # Match the field name in the model
        rating = request.POST.get("rating")

        if not comment or not rating:
            messages.error(request, "All fields are required.")
            return redirect("tournament-detail", pk=tournament.id)

        Feedback.objects.create(
            tournament=tournament,
            user=request.user,
            comment=comment,  # Use 'comment' if that's the field name in the model
            rating=rating,
        )
        print("Submitting feedback by user:", request.user)

        messages.success(request, "Feedback submitted successfully!")
        return redirect("tournament-detail", pk=tournament.id)

    return render(request, "tournaments/tournament_submit_feedback.html", {"tournament": tournament})


@login_required
def update_feedback_view(request, feedback_id):
    """
    View to handle updating feedback.
    Only the original author or an admin can update feedback.
    """
    feedback = get_object_or_404(Feedback, id=feedback_id)

    # Check if the user is authorized to update the feedback
    if feedback.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to update this feedback.")

    if request.method == "POST":
        new_comment = request.POST.get("content")
        new_rating = request.POST.get("rating")

        if not new_comment or not new_rating:
            messages.error(request, "All fields are required.")
            return redirect("update-feedback", feedback_id=feedback.id)

        # Update feedback fields
        feedback.comment = new_comment
        feedback.rating = new_rating
        feedback.save()

        messages.success(request, "Feedback updated successfully!")
        return redirect("user-feedback-list")

    return render(request, "tournaments/tournament_update_feedback.html", {"feedback": feedback})


@login_required
def delete_feedback_view(request, feedback_id):
    """
    View to handle deleting feedback.
    Only the original author or an admin can delete feedback.
    """
    feedback = get_object_or_404(Feedback, id=feedback_id)

    # Check if the user is authorized to delete the feedback
    if feedback.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to delete this feedback.")

    if request.method == "POST":
        # Delete the feedback
        feedback.delete()
        messages.success(request, "Feedback deleted successfully!")
        return redirect("user-feedback-list")

    return render(request, "tournaments/tournament_delete_feedback.html", {"feedback": feedback})


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


class ReviewListView(ListView):
    model = Review
    template_name = "games/game_reviews.html"
    context_object_name = "reviews"

    def get_queryset(self):
        game_pk = self.kwargs["pk"]
        game = get_object_or_404(Game, pk=game_pk)
        return Review.objects.filter(game=game, is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_pk = self.kwargs["pk"]
        context["game"] = get_object_or_404(Game, pk=game_pk)
        return context


@login_required
def add_to_favorites(request, pk):
    """Add a game to the current user's 'Favorites' list."""
    game = get_object_or_404(Game, pk=pk)
    favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=request.user)
    favorites_list.games.add(game)
    return redirect("favorite-list")


@login_required
def remove_from_favorites(request, pk):
    """Remove a game from the current user's 'Favorites' list."""
    game = get_object_or_404(Game, pk=pk)
    try:
        favorites_list = GameList.objects.get(name="Favorites", created_by=request.user)
        favorites_list.games.remove(game)
    except GameList.DoesNotExist:
        pass
    return redirect("favorite-list")


class FavoriteListView(LoginRequiredMixin, ListView):
    """Display the current user's favorite games."""

    model = Game
    template_name = "games/favorites_list.html"
    context_object_name = "favorite_games"

    def get_queryset(self):
        favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=self.request.user)
        return favorites_list.games.all()


@login_required
def add_to_gamelist(request, pk, list_pk):
    game = get_object_or_404(Game, pk=pk)
    game_list = get_object_or_404(GameList, pk=list_pk, created_by=request.user)
    game_list.games.add(game)
    return redirect("game-detail", pk=pk)


@login_required
def remove_from_gamelist(request, pk, list_pk):
    game = get_object_or_404(Game, pk=pk)
    game_list = get_object_or_404(GameList, pk=list_pk, created_by=request.user)
    game_list.games.remove(game)
    return redirect("game-detail", pk=pk)


# =============== Word Game Views ===============


@login_required
def wordle_game_page(request):
    # Generate a short-lived JWT for secure identification
    payload = {
        "user_id": request.user.id,
        "username": request.user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    # GitHub Pages game URL + token
    iframe_url = f"https://zhejiej.github.io/Words-Game//?token={token}"

    return render(request, "games/wordle.html", {"iframe_url": iframe_url})


@login_required
def checkers_game_view(request, pk):
    game = get_object_or_404(Checkers, id=pk)
    user = request.user

    # Match players from the fixture
    if game.player_1.user != user and game.player_2.user != user:
        return HttpResponseForbidden("You are not a player in this game.")

    # ✅ Get the latest board state
    latest_turn = CheckersTurn.objects.filter(game=game).order_by("-turn_number").first()

    if latest_turn:
        board = latest_turn.board
    else:
        default_state = [
            [0, 2, 0, 2, 0, 2, 0, 2],
            [2, 0, 2, 0, 2, 0, 2, 0],
            [0, 2, 0, 2, 0, 2, 0, 2],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0],
        ]
        board = CheckersBoard.objects.create(state=default_state)
        CheckersTurn.objects.create(game=game, board=board, turn_number=1, player=game.player_1)

    # Determine player ID for frontend
    player = game.player_1 if game.player_1.user == user else game.player_2
    turn_number = CheckersTurn.objects.filter(game=game).count() + 1

    return render(
        request,
        "games/game_checkers.html",
        {
            "game_id": game.id,
            "board_id": board.id,
            "player_id": player.id,
            "turn_number": turn_number,
        },
    )


@api_view(["POST"])
def checkers_game_update_board_state(request, board_id):
    try:
        board = CheckersBoard.objects.get(pk=board_id)
        new_state = request.data.get("state")

        if new_state is None:
            return Response({"error": "Missing 'state'"}, status=status.HTTP_400_BAD_REQUEST)

        board.state = new_state
        board.save()
        return Response({"success": True})

    except CheckersBoard.DoesNotExist:
        return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def checkers_game_get_board_state(request, board_id):
    try:
        board = CheckersBoard.objects.get(pk=board_id)
        return Response({"state": board.state})
    except CheckersBoard.DoesNotExist:
        return Response({"error": "Board not found"}, status=404)
