import random

import factory
from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from chigame.achievements.models import Achievement, UserAchievement
from chigame.api.tests.factories import GameFactory, LobbyFactory, UserFactory
from chigame.games.models import Match


class AchievementFactory(DjangoModelFactory):
    class Meta:
        model = Achievement

    name = factory.Faker("word")
    description = factory.Faker("text")
    spoiler = factory.Faker("boolean")
    rarity = factory.Faker("random_int", min=1, max=4)
    game = factory.SubFactory(GameFactory)
    threshold = factory.Faker("random_number", digits=2)  # Random number for threshold


class CompletedUserAchievementFactory(DjangoModelFactory):
    class Meta:
        model = UserAchievement

    user = factory.SubFactory(UserFactory)
    achievement = factory.SubFactory(AchievementFactory)
    pinned = factory.Faker("boolean")
    date_earned = factory.Faker("date_time_this_year")
    last_updated = factory.LazyAttribute(lambda obj: obj.date_earned)
    progress = factory.LazyAttribute(lambda obj: obj.achievement.threshold)


class UncompletedUserAchievementFactory(DjangoModelFactory):
    class Meta:
        model = UserAchievement

    user = factory.SubFactory(UserFactory)
    achievement = factory.SubFactory(AchievementFactory)
    pinned = factory.Faker("boolean")
    last_updated = factory.Faker("date_time_this_year")
    progress = factory.LazyAttribute(lambda obj: obj.achievement.threshold * random.random())


class MatchFactory(DjangoModelFactory):
    # This is pretty bad - theoretically, the lobby should determine the game and the players
    class Meta:
        model = Match

    game = factory.SubFactory(GameFactory)
    lobby = factory.SubFactory(LobbyFactory)
    date_played = factory.Faker("date_time_this_decade")

    @factory.post_generation
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
