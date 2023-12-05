from rest_framework import serializers

from chigame.games.models import Chat, Game, Lobby, Message, Tournament, User
from chigame.users.models import FriendInvitation, UserProfile


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
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


class FriendInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendInvitation
        fields = "__all__"


class MessageFeedSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["token_id", "update_on", "content", "sender"]

    def get_sender(self, obj):
        return obj.sender.name
