from django.shortcuts import get_object_or_404, render

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


def bar_chart(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    leaderboard = game.leaderboards.first()

    if not leaderboard:
        return render(request, "leaderboards/empty.html", {"game": game})

    entries = LeaderboardEntry.objects.filter(leaderboard=leaderboard).select_related("user")

    score_metric_name = f"{game.name} Points"

    leaderboard_data = []
    for entry in entries:
        # Get the score for the specified metric for this leaderboard entry
        metric_score = entry.metric_scores.filter(metric__name=score_metric_name).first()
        if metric_score:
            leaderboard_data.append({"player": entry.user.user.name, "score": metric_score.score})

    context = {
        "game": game,
        "leaderboard": leaderboard,
        "leaderboard_data": leaderboard_data,
        "score_metric_name": score_metric_name,
    }
    return render(request, "leaderboards/bar_chart.html", context)
