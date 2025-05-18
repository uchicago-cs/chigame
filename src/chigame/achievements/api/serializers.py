from rest_framework import serializers
from ..models import *

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['name', 'description', 'spoiler', 'rarity', 'game', 'threshold']

class UserAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievement
        fields = ['user', 'achievement', 'pinned', 'date_earned', 'progress']
