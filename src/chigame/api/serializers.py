from rest_framework import serializers

from chigame.games.models import Game


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name")


class GameDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"
