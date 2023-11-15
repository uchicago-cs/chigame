from rest_framework import serializers

from chigame.games.models import Game, Lobby, User


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "description", "min_players", "max_players")


class LobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lobby
        fields = (
            "id",
            "name",
            "game",
            "game_mod_status",
            "created_by",
            "members",
            "min_players",
            "max_players",
            "time_constraint",
            "lobby_created",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email")

