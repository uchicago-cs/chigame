import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory.django import DjangoModelFactory

from chigame.games.models import Game, Lobby, Match
from chigame.leaderboards.models import Leaderboard, LeaderboardEntry, Metric, MetricScore, Region, LeaderboardPrivacySetting
from chigame.users.models import UserProfile

AuthUser = get_user_model()


class AuthUserFactory(DjangoModelFactory):
    class Meta:
        model = AuthUser

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.LazyAttribute(lambda o: o.email.split("@")[0])
    # use PostGenerationMethodCall to hash the password
    password = factory.PostGenerationMethodCall("set_password", "password123")


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(AuthUserFactory)
    display_name = factory.Faker("user_name")
    bio = factory.Faker("sentence")


class RegionFactory(DjangoModelFactory):
    class Meta:
        model = Region

    continent = factory.Iterator(["North America", "Europe", "Asia"])
    country = factory.Faker("country")
    region = factory.Faker("state")


class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    min_players = 1
    max_players = 4
    complexity = factory.Iterator([1, 2, 3, 4, 5])


class LobbyFactory(DjangoModelFactory):
    class Meta:
        model = Lobby

    game = factory.SubFactory(GameFactory)
    name = factory.Faker("word")
    created_by = factory.SubFactory(AuthUserFactory)
    min_players = factory.SelfAttribute("game.min_players")
    max_players = factory.SelfAttribute("game.max_players")


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    game = factory.SubFactory(GameFactory)
    lobby = factory.SubFactory(LobbyFactory)
    date_played = factory.LazyFunction(timezone.now)


class LeaderboardFactory(DjangoModelFactory):
    class Meta:
        model = Leaderboard

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    game = factory.SubFactory(GameFactory)


class LeaderboardEntryFactory(DjangoModelFactory):
    class Meta:
        model = LeaderboardEntry

    leaderboard = factory.SubFactory(LeaderboardFactory)
    user = factory.SubFactory(UserProfileFactory)
    rank = factory.Sequence(lambda n: n + 1)


class MetricFactory(DjangoModelFactory):
    class Meta:
        model = Metric

    name = factory.Faker("word")
    unit = factory.Iterator(["points", "wins", "losses"])
    description = factory.Faker("sentence")
    game = factory.SubFactory(GameFactory)


class MetricScoreFactory(DjangoModelFactory):
    class Meta:
        model = MetricScore

    score = factory.Faker("random_int", min=0, max=100)
    leaderboard_entry = factory.SubFactory(LeaderboardEntryFactory)
    user = factory.SelfAttribute("leaderboard_entry.user")
    metric = factory.SubFactory(MetricFactory)
    match = factory.SubFactory(MatchFactory)


# This makes a default privacy setting for other factories to inherit
class LeaderboardPrivacySettingFactory(DjangoModelFactory):
    class Meta:
        model = LeaderboardPrivacySetting

    complete_opt_out = False
    display_as_anonymous = False
    user = factory.SubFactory(UserProfileFactory)
    game = None
    leaderboard = None


class GlobalPrivacySettingFactory(LeaderboardPrivacySettingFactory):
    """
    Factory for global privacy settings (no game, no leaderboard)
    """

    pass


class GamePrivacySettingFactory(LeaderboardPrivacySettingFactory):
    """
    Factory for game-level privacy settings (has game, no leaderboard)
    """

    game = factory.SubFactory(GameFactory)


class LeaderboardSpecificPrivacySettingFactory(LeaderboardPrivacySettingFactory):
    """
    Factory for leaderboard-specific privacy settings (has game and leaderboard)
    """

    leaderboard = factory.SubFactory(LeaderboardFactory)
    game = factory.SelfAttribute("leaderboard.game")
