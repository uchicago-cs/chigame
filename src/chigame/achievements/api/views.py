from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chigame.games.models import Game

from ..models import Achievement, UserAchievement
from .serializers import AchievementSerializer, UserAchievementSerializer


@api_view(["POST", "GET"])
def get_achievements(request):
    # Create an achievement
    if request.method == "POST":
        serializer = AchievementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # Get all achievements across all games
    elif request.method == "GET":
        achievements = Achievement.objects.all()
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)


@api_view(["POST", "GET"])
def get_user_achievements(request):
    # Post an achievement
    if request.method == "POST":
        serializer = UserAchievementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # Gets all user achievements
    elif request.method == "GET":
        user_achievements = UserAchievement.objects.all()
        serializer = UserAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def award_achievement(request):
    # Award an achievement for the demo game
    # Creates or gets a game called Demo Game
    # Same for the achievement and user achievement
    # Assigns the user achievement to the currently logged in user
    if request.method == "POST":
        if request.user.is_authenticated:
            popup = "F"  # Variable to decide whether a popup will occur
            game = Game.objects.get_or_create(
                name="Demo Game",
                description="Game for demonstrating achievements.",
                min_players=1,
                max_players=1,
                complexity=1,
            )[0]
            achievement = Achievement.objects.get_or_create(name="Clicked a Button", rarity=1, game=game)[0]
            user = request.user
            user_achievement = UserAchievement.objects.get_or_create(
                user=user, achievement=achievement, date_earned="2025-04-24T21:45:37.084000Z"
            )
            if user_achievement[1]:
                popup = "T"
            response_data = {"message": popup}
            return JsonResponse(response_data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def award_threshold_achievement(request):
    # Awards a threshold achievement
    # Doesn't function like an actual threshold achievement
    # but whatever
    if request.method == "POST":
        if request.user.is_authenticated:
            popup = "F"  # Variable to decide whether a popup will occur
            game = Game.objects.get_or_create(
                name="Demo Game",
                description="Game for demonstrating achievements.",
                min_players=1,
                max_players=1,
                complexity=1,
            )[0]
            threshold_achievement = Achievement.objects.get_or_create(
                name="Clicked a Button 5 Times", rarity=1, game=game, threshold=5
            )[0]
            user = request.user
            user_achievement = UserAchievement.objects.get_or_create(
                user=user, achievement=threshold_achievement, date_earned="2025-04-24T21:45:37.084000Z"
            )
            if user_achievement[1]:
                popup = "T"
            response_data = {"message": popup}
            return JsonResponse(response_data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
