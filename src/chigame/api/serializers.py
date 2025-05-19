from rest_framework import serializers

from chigame.achievements.models import Achievement, UserAchievement
from chigame.games.models import Category, Chat, Feedback, Game, Lobby, Mechanic, Message, Review, Tournament, User
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
        read_only_fields = ("user",)

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
        fields = ["id", "name", "description", "members", "group_admin_permissions"]
        read_only_fields = ["created_by", "date_created"]


class MessageFeedSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["token_id", "update_on", "content", "sender"]

    def get_sender(self, obj):
        return obj.sender.name


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "user", "title", "rating", "review", "is_public", "created_at"]
        read_only_fields = ["id", "created_at", "user"]


class UserAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievement
        fields = ["id", "user", "pinned", "date_earned", "progress"]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "name", "description", "rarity", "threshold"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "tournament", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at", "user", "tournament"]