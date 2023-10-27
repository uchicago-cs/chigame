from django.views.generic import ListView

from .models import Game


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"
