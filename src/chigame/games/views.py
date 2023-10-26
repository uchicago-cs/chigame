from django.views.generic import ListView

from .models import Game


class GameListView(ListView):
    model = Game
    queryset = Game.objects.all()
    template_name = "games/game_list.html"

def match_init(request):
    form = MatchInitForm()
    return render(request, 'games/match_form.html', {'form':form})
