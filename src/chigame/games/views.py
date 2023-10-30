from .forms import BGGSearchForm
from .models import Game
from django.shortcuts import render
from django.views.generic import ListView
import requests
import xml.etree.ElementTree as ET

BGG_BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"

class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"

# Takes a string and displays information about Board Games with title that exactly match the string via the Board Game Geek API.
# Renders a page where the specific game can be selected and its details viewed.
# This view is for demonstration purposes. Eventualy, it will be incorporated into the create game view.
def bgg_search_view(request):
    games_list = []
    form = BGGSearchForm()

    if request.method == 'POST':
        form = BGGSearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['bgg_search_term']
            url = f"{BGG_BASE_URL}search?type=boardgame&query={search_term}&exact=1"
            response = requests.get(url)
            root = ET.fromstring(response.text)

            for game in root.findall(".//item"):
                game_id = game.get("id")
                details_url = f"{BGG_BASE_URL}thing?id={game_id}&stats=1"
                details_response = requests.get(details_url)
                details_root = ET.fromstring(details_response.text)

                game_data = {
                    "id": game_id,
                    "name": details_root.find(".//name").get("value"),
                    "image": details_root.find(".//image").text,
                    "description": details_root.find(".//description").text,
                    "yearpublished": details_root.find(".//yearpublished").get("value"),
                    "boardgamepublishers": [publisher.get("value") for publisher in details_root.findall(".//link[@type='boardgamepublisher']")],
                    "minplaytime": details_root.find(".//minplaytime").get("value"),
                    "maxplaytime": details_root.find(".//maxplaytime").get("value"),
                }

                games_list.append(game_data)

    return render(request, 'games/search_results.html', {'form': form, 'games_list': games_list})
