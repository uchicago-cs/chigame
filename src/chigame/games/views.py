from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.shortcuts import render
from django.http import Http404

from .models import Game


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"


def game_browse(request):
    # This is a placeholder for the real implementation
    temp_images = [
        'https://cf.geekdo-images.com/W3Bsga_uLP9kO91gZ7H8yw__itemrep/img/IzYEUm_gWFuRFOL8gQYqGm5gU6A=/fit-in/246x300/filters:strip_icc()/pic2419375.jpg',
        'https://cf.geekdo-images.com/HkZSJfQnZ3EpS214xtuplg__imagepage/img/nLp0poXg-Y6szkicHe7U2thnwhk=/fit-in/900x600/filters:no_upscale():strip_icc()/pic2439223.jpg',
        'https://cf.geekdo-images.com/YyiFambqCNTQijYcrzXfbg__imagepage/img/ylRWhjJZyD5cVVY9gmFbjjW0Scw=/fit-in/900x600/filters:no_upscale():strip_icc()/pic829431.jpg',
    ]
    
    # We have 3 temp images, so we'll just repeat them 10 times for 30 fake games
    games = [{'image': url} for url in temp_images] * 10  
    context = {'games': games}
    return render(request, 'games/game_browse.html', context)

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

    def get_success_url(self):
        return reverse_lazy("game-detail", kwargs={"pk": self.kwargs["pk"]})
