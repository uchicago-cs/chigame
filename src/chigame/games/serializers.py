from rest_framework import serializers

from .models import CheckersBoard


class CheckersBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckersBoard
        fields = ["id", "state"]
