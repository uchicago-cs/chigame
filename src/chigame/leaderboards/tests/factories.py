from factory import Faker, SelfAttribute, SubFactory
from factory.django import DjangoModelFactory

from chigame.games.models import Game
from chigame.leaderboards.models import Leaderboard, LeaderboardPrivacySetting
from chigame.users.models import UserProfile
from chigame.users.tests.factories import UserFactory


# I'm making this because the users team doesnt have a factory for UserProfile
class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = SubFactory(UserFactory)
    display_name = Faker("user_name")


# I'm making this because the game team doesnt have a factory for Game
class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game

    name = Faker("sentence", nb_words=3)
    description = Faker("sentence")
    min_players = Faker("random_int", min=1, max=3)
    max_players = Faker("random_int", min=4, max=6)


class LeaderboardFactory(DjangoModelFactory):
    class Meta:
        model = Leaderboard

    name = Faker("sentence", nb_words=2)
    description = Faker("sentence")
    game = SubFactory(GameFactory)


# This makes a default privacy setting for other factories to inherit
class LeaderboardPrivacySettingFactory(DjangoModelFactory):
    class Meta:
        model = LeaderboardPrivacySetting

    complete_opt_out = False
    display_as_anonymous = False
    user = SubFactory(UserProfileFactory)
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

    game = SubFactory(GameFactory)


class LeaderboardSpecificPrivacySettingFactory(LeaderboardPrivacySettingFactory):
    """
    Factory for leaderboard-specific privacy settings (has game and leaderboard)
    """

    leaderboard = SubFactory(LeaderboardFactory)
    game = SelfAttribute("leaderboard.game")
