import xml.etree.ElementTree as ET

import requests
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import Game, Lobby


# =============== Games CRUD and Search Views ===============
class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"


class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"


class GameCreateView(UserPassesTestMixin, CreateView):
    model = Game
    fields = "__all__"
    template_name = "games/game_form.html"
    success_url = reverse_lazy("game-list")  # URL to redirect after successful creation

    def test_func(self):
        # Implement your logic to check if the user has permission to create a game
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True  # Used in the template to determine the mode
        return context


class GameEditView(UserPassesTestMixin, UpdateView):
    model = Game
    fields = "__all__"  # include all fields in form
    template_name = "games/game_form.html"
    raise_exception = True  # if user is not staff member, raise exception

    # if edit is successful, redirect to that game's detail page
    def get_success_url(self):
        return reverse_lazy("game-detail", kwargs={"pk": self.kwargs["pk"]})

    # check if user is staff member
    def test_func(self):
        return self.request.user.is_staff


# =============== BGG Searching =================
# The following functions involve using the BoardGameGeek API to search for games.
# API documentation: https://boardgamegeek.com/wiki/page/BGG_XML_API2
# ChiGame's documentation: https://github.com/uchicago-cs/chigame/wiki/Games-~-BoardGameGeek-(BGG)-API


def bgg_search_by_name(request):
    """
    Handles a GET request to search for board games by their exact name using the BoardGameGeek (BGG) API.
    Returns a JsonResponse of games with their details.
    """

    # Check if the request method is GET
    if request.method == "GET":
        search_term = request.GET.get("search_term")
        BGG_BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"
        url = f"{BGG_BASE_URL}search?type=boardgame&query={search_term}&exact=1"
        response = requests.get(url)
        # Parse the XML response
        root = ET.fromstring(response.text)

        # Initialize a list to store game data
        games_list = []
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

    # Construct a dictionary with the game's details, parsing various elements from the API response
    game_data = {
        "BGG_id": bgg_id,
        "name": details_root.find(".//name").get("value"),
        "image": details_root.find(".//image").text
        if details_root.find(".//image") is not None
        else "/static/images/no_picture_available.png",
        "description": details_root.find(".//description").text,
        "year_published": int(details_root.find(".//yearpublished").get("value"))
        if details_root.find(".//yearpublished") is not None
        else None,
        "min_players": details_root.find(".//minplayers").get("value"),
        "max_players": details_root.find(".//maxplayers").get("value"),
        "expected_playtime": details_root.find(".//playingtime").get("value"),
        "min_playtime": details_root.find(".//minplaytime").get("value"),
        "max_playtime": details_root.find(".//maxplaytime").get("value"),
        "suggested_age": details_root.find(".//minage").get("value"),
        "complexity": rounded_complexity,  # The rounded complexity rating of the game
    }

    return game_data


# =============== Lobby Views ===============


def lobby_list(request):
    lobbies = Lobby.objects.all()
    context = {"object_list": lobbies}
    return render(request, "games/lobby_list.html", context)


class ViewLobbyDetails(DetailView):
    model = Lobby
    template_name = "games/lobby_details.html"
    context_object_name = "lobby_detail"
