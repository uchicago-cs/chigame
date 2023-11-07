from django.db import models

from chigame.users.models import Group, User


class Game(models.Model):
    """
    A game (Chess, Checkers, etc.)
    """

    name = models.TextField()
    description = models.TextField()
    min_players = models.PositiveIntegerField()
    max_players = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Lobby(models.Model):
    """
    A lobby that users can join before starting a match.
    The match can start as soon as min_players join the lobby.
    """

    name = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="lobbies")
    min_players = models.PositiveIntegerField()
    max_players = models.PositiveIntegerField()


class Match(models.Model):
    """
    A specific match of a game, between a set of players.
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    lobby = models.OneToOneField(Lobby, on_delete=models.CASCADE)
    winners = models.ManyToManyField(User, related_name="won_matches", blank=True)
    players = models.ManyToManyField(User, through="Player")


class Player(models.Model):
    """
    A player in a match.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)


class MatchProposal(models.Model):
    """
    A proposal for a group of friends to have a match at a specific
    date/time.
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    proposer = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    proposed_time = models.DateTimeField()
    min_players = models.PositiveIntegerField()
    joined = models.ManyToManyField(User, related_name="joined_matches", blank=True)


class Tournament(models.Model):
    """
    A tournament of a game, between a set of players. Each object represents a
    single-elimination tournament.
    """

    name = models.CharField(max_length=255)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_players = models.PositiveIntegerField()
    description = models.TextField()  # not limited to 255 characters
    rules = models.TextField()  # not limited to 255 characters
    draw_rules = models.TextField()  # not limited to 255 characters
    matches = models.ManyToManyField(Match, related_name="matches")
    winners = models.ManyToManyField(User, related_name="won_tournaments", blank=True)  # allow multiple winners
    players = models.ManyToManyField(User)

    def get_all_matches(self):
        return self.matches.all()

    def get_all_winners(self):
        return self.winners.all()

    def get_all_players(self):
        return self.players.all()

    def __str__(self):  # may be changed later
        return (
            "Tournament "
            + self.name
            + ": "
            + self.game.name
            + " from "
            + self.start_date.strftime("%m/%d/%Y")
            + " to "
            + self.end_date.strftime("%m/%d/%Y")
        )
