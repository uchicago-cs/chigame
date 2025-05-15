from factory import Faker, SubFactory, post_generation
from factory.django import DjangoModelFactory

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
