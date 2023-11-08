from rest_framework import serializers

from chigame.games.models import Game
from chigame.users.models import UserProfile


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "description", "min_players", "max_players")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "display_name", "bio", "date_joined")
