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
    date_played = models.DateTimeField()
    players = models.ManyToManyField(User, through="Player")


class Player(models.Model):
    """
    A player in a match.
    """

    WIN = 0
    DRAW = 1
    LOSE = 2
    WITHDRAWAL = 3

    OUTCOMES = (
        (WIN, "win"),
        (DRAW, "draw"),
        (LOSE, "lose"),
        (WITHDRAWAL, "withdrawal"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.TextField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)
    outcome = models.PositiveSmallIntegerField(choices=OUTCOMES)
    victory_type = models.TextField(blank=True, null=True)


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
