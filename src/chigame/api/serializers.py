from rest_framework import serializers

from chigame.games.models import Game, User


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "description", "min_players", "max_players")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "email")


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email")
