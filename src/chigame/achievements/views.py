from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Achievement, UserAchievement


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
