from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import *
from .serializers import *

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
    # Awards an achievement to the user
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
