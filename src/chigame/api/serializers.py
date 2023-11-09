from rest_framework import serializers

from chigame.games.models import Game
from chigame.users.models import User


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "description", "min_players", "max_players")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email")
