from django.db import models
from django.utils import timezone

from chigame.users.models import Group, User


class Game(models.Model):
    """
    A game like Chess, Checkers, etc.
    """

    # Basic information
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.URLField(default="/static/images/no_picture_available.png")
    year_published = models.PositiveIntegerField(null=True)

    # Gameplay information
    rules = models.TextField(null=True)

    min_players = models.PositiveIntegerField()
    max_players = models.PositiveIntegerField()
    suggested_age = models.PositiveSmallIntegerField(
        null=True
    )  # Minimum recommendable age. For example, 8+ would be 8.

    expected_playtime = models.PositiveIntegerField(null=True)  # In Minutes
    min_playtime = models.PositiveIntegerField(null=True)
    max_playtime = models.PositiveIntegerField(null=True)

    complexity = models.PositiveSmallIntegerField(null=True)  # 1-5, 1 being the easiest
    category = models.ManyToManyField("Category", related_name="games")
    mechanics = models.ManyToManyField("Mechanic", related_name="games")

    # BGG information
    BGG_id = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    """
    A person associated with a game, such as a designer or artist.
    """

    DESIGNER = 1
    ARTIST = 2

    ROLE_CHOICES = (
        (DESIGNER, "Designer"),
        (ARTIST, "Artist"),
    )

    name = models.CharField(max_length=255)
    person_role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)
    games = models.ManyToManyField(Game, related_name="people")

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """
    A publisher of a game.
    """

    name = models.CharField(max_length=255)
    games = models.ManyToManyField(Game, related_name="publishers")
    website = models.URLField(null=True)
    year_established = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Category of the game like Strategy, Adventure, etc.
    See a full list of options: https://boardgamegeek.com/browse/boardgamecategory
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name


class Mechanic(models.Model):
    """
    Mechanic of the game like Dice Rolling, Hand Management, etc.
    See a full list of options: https://boardgamegeek.com/browse/boardgamemechanic
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)

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
    MODS = ((Default_game, "Default Game"), (Modified_game, "Modified Game"))

    match_status = models.PositiveSmallIntegerField(choices=STATUS, default=1)
    name = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    game_mod_status = models.PositiveSmallIntegerField(choices=MODS, default=1)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="lobbies")
    min_players = models.PositiveIntegerField()
    max_players = models.PositiveIntegerField()
    time_constraint = models.PositiveIntegerField(default=300)
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
