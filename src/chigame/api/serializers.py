from rest_framework import serializers

from chigame.games.models import Game, Notification, Tournament
from chigame.users.models import User


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "description", "min_players", "max_players")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("recipients", "content", "timestamp")


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = (
            "game",
            "start_date",
            "end_date",
            "max_players",
            "description",
            "rules",
            "draw_rules",
            "matches",
            "winners",
            "players",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "name")
        extra_kwargs = {"password": {"write_only": True}}
