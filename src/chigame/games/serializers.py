from rest_framework import serializers

from .models import Checkers, CheckersBoard, CheckersTurn, Player


class CheckersBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckersBoard
        fields = ["id", "state"]


class CheckersTurnSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Checkers.objects.all())
    board = serializers.PrimaryKeyRelatedField(queryset=CheckersBoard.objects.all())
    player = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all())

    class Meta:
        model = CheckersTurn
        fields = ["id", "game", "board", "player", "turn_number", "snapshot"]
