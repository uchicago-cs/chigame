from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view

from ..models import Achievement, UserAchievement
from chigame.games.models import Game
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
          game = Game.objects.get_or_create(
              name = "Demo Game",
              description = "Game for demonstrating achievements.",
              min_players = 1,
              max_players = 1,
              complexity = 1)[0]
          achievement = Achievement.objects.get_or_create(
              name = "Clicked a Button",
              rarity = 1,
              game = game)[0]
          user = request.user
          user_achievement = UserAchievement.objects.get_or_create(
              user = user,
              achievement = achievement,
              date_earned = "2025-04-24T21:45:37.084000Z")
          response_data = {'message': 'Button press received'}
          return JsonResponse(response_data)
