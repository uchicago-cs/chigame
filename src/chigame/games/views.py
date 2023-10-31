from django.views.generic import DetailView, ListView

from .models import Game


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"


class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"
