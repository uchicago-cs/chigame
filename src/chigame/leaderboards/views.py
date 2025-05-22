from django.shortcuts import get_object_or_404, render

from chigame.games.models import Game
from chigame.leaderboards.models import LeaderboardEntry, Region
from chigame.users.models import UserProfile


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


def landing_page_view(request):
    # temp fallback for logged-out user: no LeaderboardEntries displayed
    entries = []

    default_view_metric = None
    anonymity = None

    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        entries = (
            LeaderboardEntry.objects.filter(user=user_profile).select_related("leaderboard__game").order_by("rank")[:5]
        )

        # We will likely need to add the following fields to the User model (cc User team):

        # user = User.objects.get(pk=request.user.pk)
        # default_view_metric = user.default_metric
        # anonymity = user_profile.anonymity_setting

    return render(
        request,
        "leaderboards/landing_page.html",
        {
            "entries": entries,
            "default_view_metric": default_view_metric,
            "anonymity": anonymity,
        },
    )


def user_profile_view(request, leaderboard_entry_id):
    pass


def select_default_view_metric(request):
    pass


def select_anonymity(request):
    pass


def select_game_view_metric(request):
    pass


# def select_region(request):
#     pass -- from django.urls import path
