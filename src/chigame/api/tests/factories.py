from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from chigame.games.models import Category, Game, Mechanic


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = Faker("word")
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
    max_players = Faker("pyint", min_value=1, max_value=10)

    suggested_age = Faker("pyint", min_value=1, max_value=18)

    expected_playtime = Faker("pyint", min_value=1, max_value=1000)
    min_playtime = Faker("pyint", min_value=1, max_value=1000)
    max_playtime = Faker("pyint", min_value=1, max_value=1000)

    complexity = Faker("pyint", min_value=1, max_value=5)

    BGG_id = Faker("pyint", min_value=1, max_value=1000000)

    @post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for c in extracted:
                self.category.add(c)
        else:
            # Add a random category if none are specified
            self.category.add(CategoryFactory())

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
