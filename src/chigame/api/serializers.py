from rest_framework import serializers

from chigame.games.models import Game, Lobby, Message, User


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


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.EmailField(write_only=True, source="sender")

    class Meta:
        model = Message
        fields = ("update_on", "content", "sender", "chat")

    def create(self, validated_data):
        sender_email = validated_data.pop("sender")
        user = User.objects.get(email=sender_email)
        validated_data["sender"] = user
        message = Message.objects.create(**validated_data)
        return message
