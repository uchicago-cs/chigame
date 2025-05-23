from django.shortcuts import get_object_or_404, render

from chigame.games.models import Game
from chigame.leaderboards.models import LeaderboardEntry, Region, Metric

def get_tier_info(score, metric_name):
    tier_name = "Unranked"
    tier_badge = ""

    if "Points" in metric_name:
        if score >= 50000:
            tier_name = "Diamond"
            tier_badge = "💎"
        elif score >= 20000:
            tier_name = "Platinum"
            tier_badge = "✨"
        elif score >= 9000:
            tier_name = "Gold"
            tier_badge = "🥇"
        elif score >= 7000:
            tier_name = "Silver"
            tier_badge = "🥈"
        elif score > 5000:
            tier_name = "Bronze"
            tier_badge = "🥉"
    elif "Games Won" in metric_name:
        if score >= 30:
            tier_name = "Grandmaster"
            tier_badge = "👑"
        elif score >= 25:
            tier_name = "Master"
            tier_badge = "🌟"
        elif score >= 20:
            tier_name = "Expert"
            tier_badge = "🛡️"
        else:
            tier_name = "Novice"
            tier_badge = "🌱"
    elif "Time Played" in metric_name:
        if score >= 80:
            tier_name = "Veteran"
            tier_badge = "🕰️"
        elif score >= 60:
            tier_name = "Dedicated"
            tier_badge = "⏳"
        elif score >= 40:
            tier_name = "Active"
            tier_badge = "⚡"
        elif score >= 10:
            tier_name = "Casual"
            tier_badge = "☕"
        else:
            tier_name = "Newbie"
            tier_badge = "🐣"

    return tier_name, tier_badge

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
        metric_score = entry.metric_scores.filter(metric__name=score_metric_name).first()
        if metric_score:
            tier_name, tier_badge = get_tier_info(metric_score.score, score_metric_name)
            leaderboard_data.append({
                "player": entry.user.user.name,
                "score": metric_score.score,
                "tier_name": tier_name,
                "tier_badge": tier_badge,
            })
    leaderboard_data.sort(key=lambda item: item["score"], reverse=True)

    context = {
        "game": game,
        "leaderboard": leaderboard,
        "leaderboard_data": leaderboard_data,
        "score_metric_name": score_metric_name,
    }
    return render(request, "leaderboards/bar_chart.html", context)

def top_time_played_bar_chart(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    leaderboard = game.leaderboards.filter(name__icontains="Time Played").first()

    if not leaderboard:
        return render(request, "leaderboards/empty.html", {"game": game, "message": f"No 'Time Played' leaderboard found for {game.name}."})

    entries = LeaderboardEntry.objects.filter(leaderboard=leaderboard).select_related("user")

    time_played_metric = Metric.objects.filter(game=game, name__icontains="Time Played").first()

    if not time_played_metric:
        return render(request, "leaderboards/error.html", {"message": f"No 'Time Played' metric found for {game.name}."})

    leaderboard_data = []
    for entry in entries:
        metric_score = entry.metric_scores.filter(metric=time_played_metric).first()
        if metric_score:
            tier_name, tier_badge = get_tier_info(metric_score.score, time_played_metric.name)
            leaderboard_data.append({
                "player": entry.user.user.name,
                "score": metric_score.score,
                "tier_name": tier_name,
                "tier_badge": tier_badge,
            })

    leaderboard_data.sort(key=lambda item: item['score'], reverse=True)

    context = {
        "game": game,
        "leaderboard": leaderboard,
        "leaderboard_data": leaderboard_data,
        "score_metric_name": time_played_metric.name,
    }
    return render(request, "leaderboards/bar_chart.html", context)

def top_games_won_bar_chart(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    leaderboard = game.leaderboards.filter(name__icontains="Games Won").first()

    if not leaderboard:
        return render(request, "leaderboards/empty.html", {"game": game, "message": f"No 'Games Won' leaderboard found for {game.name}."})

    entries = LeaderboardEntry.objects.filter(leaderboard=leaderboard).select_related("user")

    games_won_metric = Metric.objects.filter(game=game, name__icontains="Games Won").first()

    if not games_won_metric:
        return render(request, "leaderboards/error.html", {"message": f"No 'Games Won' metric found for {game.name}."})

    leaderboard_data = []
    for entry in entries:
        metric_score = entry.metric_scores.filter(metric=games_won_metric).first()
        if metric_score:
            tier_name, tier_badge = get_tier_info(metric_score.score, games_won_metric.name)
            leaderboard_data.append({
                "player": entry.user.user.name,
                "score": metric_score.score,
                "tier_name": tier_name,
                "tier_badge": tier_badge,
            })

    leaderboard_data.sort(key=lambda item: item['score'], reverse=True)

    context = {
        "game": game,
        "leaderboard": leaderboard,
        "leaderboard_data": leaderboard_data,
        "score_metric_name": games_won_metric.name,
    }
    return render(request, "leaderboards/bar_chart.html", context)
