from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from chigame.games.models import Game
from chigame.users.models import User

from .models import Achievement, UserAchievement


def get_recent_achievements(pk, limit=5):
    """
    Helper function to get the most recent achievements for a user. This function should be used to call
    the most recent achievements to be displayed on the user's profile page.
    Args:
        pl (int): The primary key of the user whose achievements are to be fetched.
        limit (int): The maximum number of recent achievements to fetch. Default is 5.
    """
    return UserAchievement.objects.filter(user_id=pk).order_by("-date_earned")[:limit]


def demo_game(request):
    return render(request, "achievements/demo_game.html")


@login_required
def toggle_pin_achievement(request, achievement_id):
    """
    AJAX view to toggle whether an achievement is pinned for the current user
    """
    if request.method == "POST":
        achievement = get_object_or_404(Achievement, id=achievement_id)

        # Use get_or_create with defaults to avoid duplicates
        user_achievement, created = UserAchievement.objects.get_or_create(
            user=request.user, achievement=achievement, defaults={"date_earned": timezone.now(), "pinned": True}
        )

        # If not newly created, just toggle the pinned status
        if not created:
            user_achievement.pinned = not user_achievement.pinned
            user_achievement.save(update_fields=["pinned"])  # Only update the pinned field

        return JsonResponse({"status": "success", "pinned": user_achievement.pinned})

    return JsonResponse({"status": "error"}, status=400)


def get_pinned_achievements(request):
    # Change from request.user.profile to request.user
    pinned_achievements = UserAchievement.objects.filter(user=request.user, pinned=True).select_related(
        "achievement", "achievement__game"
    )

    data = {
        "pinned_achievements": [
            {
                "id": ua.achievement.id,
                "name": ua.achievement.name,
                "description": ua.achievement.description,
                "game_name": ua.achievement.game.name,
                "rarity": ua.achievement.rarity,
                "date_earned": ua.date_earned.strftime("%B %d, %Y") if ua.date_earned else "Not unlocked",
            }
            for ua in pinned_achievements
        ]
    }
    return JsonResponse(data)


def user_achievements(request, username=None):
    """
    Display a user's achievements page.
    If username is provided, show that user's achievements.
    Otherwise, show the logged-in user's achievements.
    """
    if username:
        # If a username is provided in the URL, get that user's profile
        target_user = get_object_or_404(User, username=username)  # Renamed to avoid confusion with request.user
        viewing_own_profile = target_user == request.user
    else:
        # If no username is provided, show the logged-in user's achievements
        target_user = request.user
        viewing_own_profile = True

    # Get all games
    games = Game.objects.all()

    # Get user's join date for display
    join_date = target_user.date_joined.strftime("%B %Y")

    # Get all user achievements for the target user (do this once, outside the game loop)
    user_achievements_map = {}
    user_achievements = UserAchievement.objects.filter(user=target_user).select_related("achievement")

    # Count truly unlocked achievements
    actually_unlocked_count = 0
    for ua in user_achievements:
        achievement = ua.achievement
        if achievement.threshold is None or achievement.threshold == 0:
            # Non-progress based achievement
            if ua.date_earned is not None:
                actually_unlocked_count += 1
        elif ua.progress is not None and achievement.threshold > 0:
            # Progress-based achievement
            if ua.progress >= achievement.threshold:
                actually_unlocked_count += 1

    # Create a lookup map for quick access to user achievements
    for ua in user_achievements:
        user_achievements_map[ua.achievement.id] = ua

    # Pre-calculate achievement counts for all games
    game_achievement_counts = {}
    for game in games:
        count = Achievement.objects.filter(game=game).count()
        game_achievement_counts[game.id] = count
        # Add the total_achievements attribute to each game
        game.total_achievements = count

    # Process games
    games_with_achievements_data = []

    for game_instance in games:
        # Get all achievements for this game - clean, without complex annotations
        achievements_for_game = Achievement.objects.filter(game=game_instance).order_by("rarity")

        # Skip games with no achievements
        if not achievements_for_game.exists():
            continue

        processed_achievements_for_game = []

        for achievement in achievements_for_game:
            # Check if the user has this achievement in our lookup map
            user_achievement = user_achievements_map.get(achievement.id)

            if user_achievement:
                # User has some record of this achievement
                if achievement.threshold is None or achievement.threshold == 0:
                    # For non-progress based achievements
                    is_unlocked = user_achievement.date_earned is not None
                else:
                    # For progress-based achievements
                    is_unlocked = (
                        user_achievement.progress is not None and user_achievement.progress >= achievement.threshold
                    )

                progress = user_achievement.progress or 0
                pinned = user_achievement.pinned
                date_earned = user_achievement.date_earned
            else:
                # User has no record of this achievement
                is_unlocked = False
                progress = 0
                pinned = False
                date_earned = None

            # Add template-specific attributes
            achievement.is_unlocked_for_template = is_unlocked
            achievement.progress_for_template = progress
            achievement.pinned_for_template = pinned
            achievement.date_earned_for_template = date_earned

            # Calculate percentage of players with this achievement
            unlocked_by_users_count = UserAchievement.objects.filter(
                achievement=achievement, date_earned__isnull=False
            ).count()

            total_users = User.objects.count()
            if total_users > 0:
                achievement.percent_of_players = round(unlocked_by_users_count / total_users * 100)
            else:
                achievement.percent_of_players = 0

            # Calculate progress percentage for display
            if (
                achievement.progress_for_template is not None
                and achievement.threshold is not None
                and achievement.threshold > 0
            ):
                achievement.progress_percent_for_template = min(
                    100, (achievement.progress_for_template / achievement.threshold) * 100
                )
            else:
                achievement.progress_percent_for_template = 100 if is_unlocked else 0

            processed_achievements_for_game.append(achievement)

        # Calculate game-specific progress
        game_truly_unlocked_count = sum(1 for ach in processed_achievements_for_game if ach.is_unlocked_for_template)
        total_game_achievements = game_achievement_counts[game_instance.id]

        game_progress_percentage = (
            (game_truly_unlocked_count / total_game_achievements * 100) if total_game_achievements > 0 else 0
        )

        # Add game data to the list
        games_with_achievements_data.append(
            {
                "game": game_instance,  # game_instance already has total_achievements attribute set
                "achievements": processed_achievements_for_game,
                "progress": game_progress_percentage,
                "truly_unlocked_for_game": game_truly_unlocked_count,
                "total_achievements": total_game_achievements,
            }
        )

    # Get pinned achievements for the pinned tab
    pinned_achievements_qs = UserAchievement.objects.filter(user=target_user, pinned=True).select_related(
        "achievement", "achievement__game"
    )

    # Calculate overall stats
    total_system_achievements = Achievement.objects.count()
    overall_unlocked_achievements = actually_unlocked_count
    overall_progress = (
        (overall_unlocked_achievements / total_system_achievements * 100) if total_system_achievements > 0 else 0
    )

    context = {
        "user_profile": target_user,
        "viewing_own_profile": viewing_own_profile,
        "join_date": join_date,
        "games_with_achievements": games_with_achievements_data,
        "overall_stats": {
            "total": total_system_achievements,
            "unlocked": overall_unlocked_achievements,
            "progress": overall_progress,
        },
        "pinned_achievements": pinned_achievements_qs,
    }

    return render(request, "achievements/user_achievements.html", context)
