from .models import UserAchievement
from django.shortcuts import render


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
