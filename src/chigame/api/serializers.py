from rest_framework import serializers

from chigame.games.models import (
  Category, 
  Chat, 
  Game, 
  Lobby, 
  Mechanic, 
  Message, 
  Tournament, 
  User,
)

from chigame.users.models import Group


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


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
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "name", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["email"],
            validated_data["password"],
            name=validated_data["name"],
            username=validated_data["username"],
        )

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MechanicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mechanic
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.EmailField(write_only=True)

    tournament = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = ("update_on", "content", "sender", "tournament")

    def create(self, validated_data):
        sender_email = validated_data.pop("sender")
        tournament_id = validated_data.pop("tournament")

        tournament = Tournament.objects.get(pk=tournament_id)
        chat = Chat.objects.get(tournament=tournament)

        user = User.objects.get(email=sender_email)
        validated_data["sender"] = user
        validated_data["chat"] = chat

        message = Message.objects.create(**validated_data)
        return message


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class MessageFeedSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["token_id", "update_on", "content", "sender"]

    def get_sender(self, obj):
        return obj.sender.name
