from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from .models import Game


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"
    
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
    success_url = reverse_lazy("game-list")
    