from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from chigame.games.models import Game
from chigame.leaderboards.models import Leaderboard, LeaderboardEntry, LeaderboardPrivacySetting

from .forms import LeaderboardPrivacySettingForm


def leaderboard_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    leaderboard = game.leaderboards.first()

    if not leaderboard:
        return render(request, "leaderboards/empty.html", {"game": game})

    entries = (
        LeaderboardEntry.objects.filter(leaderboard=leaderboard)
        # .select_related("user", "user__region")
        .order_by("rank")
    )

    return render(
        request, "leaderboards/leaderboard.html", {"game": game, "leaderboard": leaderboard, "entries": entries}
    )


@login_required
def privacy_setting_list(request):
    """
    Show all settings for the current user.
    """
    # Getting user and their settings
    userprofile = request.user.userprofile
    settings = LeaderboardPrivacySetting.objects.filter(user=userprofile)

    available_games = []
    available_leaderboards = []

    # for the display when the user does not have any settings
    if not settings.exists():
        # Get games that don't have privacy settings yet
        games_with_settings = settings.values_list("game_id", flat=True).distinct()
        available_games = Game.objects.exclude(id__in=games_with_settings)

        # Get 10 sample leaderboards
        available_leaderboards = Leaderboard.objects.all()[:10]

    context = {
        "settings": settings,
        "available_games": available_games,
        "available_leaderboards": available_leaderboards,
    }

    return render(request, "leaderboards/privacy_setting_list.html", context)


@login_required
def privacy_setting_manage(request, game_id=None, leaderboard_id=None):
    """
    A way to create or update a privacy setting.
    """
    userprofile = request.user.userprofile

    # Finding the scope of the setting
    game = None
    if game_id:
        game = get_object_or_404(Game, id=game_id)

    leaderboard = None
    if leaderboard_id:
        leaderboard = get_object_or_404(Leaderboard, id=leaderboard_id, game=game)

    # Get the setting if it exists
    setting = LeaderboardPrivacySetting.objects.filter(user=userprofile, game=game, leaderboard=leaderboard).first()

    if request.method == "POST":
        form = LeaderboardPrivacySettingForm(request.POST, instance=setting)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = userprofile
            form.game = game
            form.leaderboard = leaderboard
            form.save()
            return redirect(request.path)
    else:
        form = LeaderboardPrivacySettingForm(instance=setting)

    # better titles
    if leaderboard:
        scope = f"Leaderboard: {leaderboard.name}"
    elif game:
        scope = f"Game: {game.name}"
    else:
        scope = "Global"

    context = {"form": form, "scope": scope}

    return render(request, "leaderboards/privacy_setting_form.html", context)


@login_required
def privacy_setting_delete(request, pk):
    """
    delete a privacy setting.
    """
    userprofile = request.user.userprofile
    setting = get_object_or_404(LeaderboardPrivacySetting, pk=pk, user=userprofile)
    if request.method == "POST":
        setting.delete()
        return redirect(reverse("privacy-list"))

    context = {"setting": setting}

    return render(request, "leaderboards/privacy_setting_confirm_delete.html", context)
