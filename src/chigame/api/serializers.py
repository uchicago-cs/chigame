from rest_framework import serializers

from chigame.achievements.models import Achievement, UserAchievement
from chigame.chat.models import LiveChat
from chigame.games.models import (
    Announcement,
    Category,
    Chat,
    Checkers,
    CheckersBoard,
    CheckersTurn,
    Feedback,
    Game,
    GameData,
    GameList,
    InteractiveFictionGame,
    Lobby,
    Match,
    MatchProposal,
    Mechanic,
    Message,
    Person,
    Player,
    Publisher,
    Review,
    Tournament,
    User,
)
from chigame.leaderboards.models import MetricScore
from chigame.users.models import Group, UserProfile


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
        fields = ["id", "user", "pinned", "date_earned", "last_updated", "progress"]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "name", "description", "rarity", "threshold"]


class MetricScoreSerializer(serializers.ModelSerializer):
    metric_id = serializers.IntegerField(write_only=True)
    match_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MetricScore
        fields = ["id", "score", "user", "metric", "match", "leaderboard_entry", "metric_id", "match_id"]
        read_only_fields = ["id", "user", "metric", "match", "leaderboard_entry"]

    def validate_score(self, value):
        if value < 0:
            raise serializers.ValidationError("Score must be a positive integer.")
        return value


class GameLeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    score = serializers.IntegerField(source="max_score")

    class Meta:
        model = MetricScore
        fields = ["id", "username", "score"]

    def get_username(self, obj):
        user_profile = UserProfile.objects.get(id=obj["user"])
        return user_profile.user.username


class PopUpInfoSerializer(serializers.Serializer):
    min_players = serializers.IntegerField()
    max_players = serializers.IntegerField()
    complexity = serializers.FloatField()
    min_playtime = serializers.IntegerField()
    max_playtime = serializers.IntegerField()
    description = serializers.CharField()


class GameDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameData
        fields = ["id", "game", "key", "value", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "tournament", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at", "user", "tournament"]


class GameReviewStatsSerializer(serializers.Serializer):
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    popularity = serializers.IntegerField()
    read_only_fields = ["id", "created_at", "user", "tournament"]


class LiveChatSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = LiveChat
        fields = ["id", "name", "users"]


class InteractiveFictionGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveFictionGame
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    games = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Person
        fields = ["id", "name", "person_role", "games"]

     
class PublisherSerializer(serializers.ModelSerializer):
    games = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Publisher
        fields = ["id", "name", "games", "website", "year_established"]


class MatchSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, source="player_set", read_only=True)
    game = serializers.PrimaryKeyRelatedField(read_only=True)
    lobby = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Match
        fields = ["id", "game", "lobby", "date_played", "players"]


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Player
        fields = [
            "id",
            "user",
            "match",
            "team",
            "role",
            "outcome",
            "victory_type",
        ]


class MatchProposalSerializer(serializers.ModelSerializer):
    proposer = UserSerializer(read_only=True)
    joined = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = MatchProposal
        fields = [
            "id",
            "game",
            "proposer",
            "group",
            "proposed_time",
            "min_players",
            "joined",
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    recipients = UserSerializer(many=True, read_only=True)
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "recipients",
            "content",
            "sender",
            "timestamp",
            "sent",
            "type",
        ]

class GameListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    games = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = GameList
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "games",
            "created_at",
            "updated_at",
        ]


class CheckersSerializer(serializers.ModelSerializer):
    player_1 = PlayerSerializer(read_only=True)
    player_2 = PlayerSerializer(read_only=True)
    winner = PlayerSerializer(read_only=True)

    class Meta:
        model = Checkers
        fields = [
            "id",
            "player_1",
            "player_2",
            "winner",
            "start_time",
            "end_time",
        ]


class CheckersBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckersBoard
        fields = ["id", "state"]


class CheckersTurnSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = CheckersTurn
        fields = ["id", "game", "board", "turn_number", "player"]

