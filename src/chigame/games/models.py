from django.db import models
from django.utils import timezone

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

    Lobbied = 1
    Viewable = 2
    Finished = 3
    STATUS = ((Lobbied, "Lobbied"), (Viewable, "In-Progress"), (Finished, "Finished"))

    Default_game = 1
    Modified_game = 2
    MODIFICATIONS = ((Default_game, "Default Game"), (Modified_game, "Modified Game"))

    match_status = models.PositiveSmallIntegerField(choices=STATUS, default="Lobbied")
    name = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    game_modification_status = models.PositiveSmallIntegerField(choices=MODIFICATIONS, default="Default Game")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="lobbies")
    min_players = models.PositiveIntegerField()
    max_players = models.PositiveIntegerField()
    time_constraint = models.PositiveIntegerField(default=3)
    lobby_created = models.DateTimeField(default=timezone.now)


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
