import random

from django.utils import timezone
from factory import Faker, Iterator, LazyAttribute, LazyFunction, Sequence, SubFactory, post_generation
from factory.django import DjangoModelFactory

from chigame.games.models import Category, Chat, Game, Lobby, Mechanic, Tournament
from chigame.users.models import User


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = Sequence(lambda n: f"Category {n + 1}")
    description = Faker("text", max_nb_chars=200)


class MechanicFactory(DjangoModelFactory):
    class Meta:
        model = Mechanic

    name = Faker("word")
    description = Faker("text", max_nb_chars=200)


class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game

    name = Faker("sentence", nb_words=3)
    description = Faker("text", max_nb_chars=200)
    year_published = Faker("pyint", min_value=1900, max_value=2023)

    rules = Faker("text", max_nb_chars=1000)

    min_players = Faker("pyint", min_value=1, max_value=10)

    # LazyAttribute allows setting a field's value based on other fields at runtime
    # In this case, we want max_players to be at least min_players, but no more than 10
    max_players = LazyAttribute(lambda x: random.randint(x.min_players, 10))

    suggested_age = Faker("pyint", min_value=1, max_value=18)

    # Ensure min_playtime is not greater than max_playtime
    min_playtime = Faker("pyint", min_value=1, max_value=1000)
    max_playtime = LazyAttribute(lambda x: random.randint(x.min_playtime, 1000))
    expected_playtime = LazyAttribute(lambda x: random.randint(x.min_playtime, x.max_playtime))

    complexity = Faker("pyint", min_value=1, max_value=5)

    BGG_id = Faker("pyint", min_value=1, max_value=1000000)

    @post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for c in extracted:
                self.categories.add(c)
        else:
            # Add a random category if none are specified
            self.categories.add(CategoryFactory())

    @post_generation
    def mechanics(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for mechanic in extracted:
                self.mechanics.add(mechanic)
        else:
            # Add a random mechanic if none are specified
            self.mechanics.add(MechanicFactory())


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    name = Faker("name")
    email = Faker("email")
    password = Faker("password")


class TournamentFactory(DjangoModelFactory):
    class Meta:
        model = Tournament

    name = Faker("word")
    game = SubFactory(GameFactory)
    registration_start_date = Faker("date_this_year")
    registration_end_date = Faker("date_this_year")
    tournament_start_date = Faker("date_this_year")
    tournament_end_date = Faker("date_this_year")
    max_players = Faker("pyint", min_value=1, max_value=1000)
    description = Faker("text")
    rules = Faker("text")
    draw_rules = Faker("text")
    num_winner = Faker("pyint", min_value=1, max_value=1000)


class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat

    tournament = SubFactory(TournamentFactory)


class LobbyFactory(DjangoModelFactory):
    class Meta:
        model = Lobby

    match_status = Iterator([Lobby.Lobbied, Lobby.Viewable, Lobby.Finished])

    name = Sequence(lambda n: f"lobby_{n}")
    game = SubFactory(GameFactory)

    game_mod_status = Iterator([Lobby.Default_game, Lobby.Modified_game])

    created_by = SubFactory(UserFactory)
    min_players = LazyAttribute(lambda x: random.randint(2, 6))
    max_players = LazyAttribute(lambda o: random.randint(o.min_players, 10))
    time_constraint = LazyAttribute(lambda x: random.randint(100, 500))
    lobby_created = LazyFunction(timezone.now)
    created_by = SubFactory(UserFactory)
    lobby_created = Faker("date_time_this_decade")
