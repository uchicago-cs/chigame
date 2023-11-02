from rest_framework import serializers

from chigame.games.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("name", "description", "min_players", "max_players")
