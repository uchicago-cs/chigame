from django.utils import timezone
from factory import Faker, LazyFunction, Sequence, SubFactory, post_generation
from factory.django import DjangoModelFactory

from chigame.achievements.models import Achievement, UserAchievement
from chigame.api.tests.factories import GameFactory, LobbyFactory, UserFactory
from chigame.games.models import Match


class MatchFactory(DjangoModelFactory):
    # This is pretty bad - theoretically, the lobby should determine the game and the players
    class Meta:
        model = Match

    game = SubFactory(GameFactory)
    lobby = SubFactory(LobbyFactory)
    date_played = Faker("date_time_this_decade")

    @post_generation
    def players(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # Add players to the match
            for player in extracted:
                self.players.add(player)
        else:
            # Add
            self.players.add(UserFactory())


class AchievementFactory(DjangoModelFactory):
    class Meta:
        model = Achievement

    name = Sequence(lambda n: f"Achievement {n}")
    description = "Test description"
    spoiler = False
    rarity = Achievement.Rarity.COMMON
    game = SubFactory(GameFactory)
    threshold = 1.0


class UserAchievementFactory(DjangoModelFactory):
    class Meta:
        model = UserAchievement

    user = SubFactory(UserFactory)
    achievement = SubFactory(AchievementFactory)
    pinned = False
    date_earned = LazyFunction(timezone.now)
    progress = 1.0
