import factory
from factory.django import DjangoModelFactory

from chigame.achievements.models import Achievement, User, UserAchievement
from chigame.api.tests.factories import GameFactory, LobbyFactory, UserFactory
from chigame.games.models import Match


# General user factory
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "password")


class AchievementFactory(DjangoModelFactory):
    class Meta:
        model = Achievement

    name = factory.Faker("word")
    description = factory.Faker("text")
    spoiler = factory.Faker("boolean")
    rarity = factory.Faker("random_int", min=1, max=4)
    game = factory.SubFactory(GameFactory)
    threshold = factory.Faker("random_number", digits=2)  # Random number for threshold


class UserAchievementFactory(DjangoModelFactory):
    class Meta:
        model = UserAchievement

    user = factory.SubFactory(UserFactory)
    achievement = factory.SubFactory(AchievementFactory)
    pinned = factory.Faker("boolean")
    date_earned = factory.Faker("date_time_this_year")
    progress = factory.Faker("random_number", digits=2)  # Random number for progress


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
