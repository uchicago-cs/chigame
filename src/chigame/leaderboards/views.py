from django.shortcuts import render, get_object_or_404
from chigame.games.models import Game
from chigame.leaderboard.models import Leaderboard, LeaderboardEntry

def leaderboard_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    leaderboard = game.leaderboards.first()  # For now, pick the first leaderboard

    if not leaderboard:
        return render(request, "leaderboards/empty.html", {"game": game})

    entries = LeaderboardEntry.objects.filter(
        leaderboard=leaderboard
    ).select_related("user", "user__region").order_by("rank")

    return render(request, "leaderboards/leaderboard.html", {
        "game": game,
        "leaderboard": leaderboard,
        "entries": entries
    })
