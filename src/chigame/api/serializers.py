from rest_framework import serializers

from chigame.games.models import Game, Lobby, Tournament
from chigame.users.models import User


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "description", "min_players", "max_players")


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
