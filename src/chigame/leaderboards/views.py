from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from chigame.games.models import Game
from chigame.leaderboards.models import LeaderboardEntry, Region


def leaderboard_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    leaderboard = game.leaderboards.first()

    if not leaderboard:
        return render(request, "leaderboards/empty.html", {"game": game})

    entries = (
        LeaderboardEntry.objects.filter(leaderboard=leaderboard).select_related("user", "region").order_by("rank")
    )

    region_param = request.GET.get("region")
    if region_param:
        entries = entries.filter(region__region=region_param)

    available_regions = Region.objects.values_list("region", flat=True).distinct()

    return render(
        request,
        "leaderboards/leaderboard.html",
        {
            "game": game,
            "leaderboard": leaderboard,
            "entries": entries,
            "regions": available_regions,
            "selected_region": region_param,
        },
    )
