from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from chigame.users.models import Group, Notification, User


class Game(models.Model):
    """
    A game like Chess, Checkers, etc.
    """

    # ================ BASIC INFORMATION ================
    name = models.TextField()
    description = models.TextField()
    year_published = models.IntegerField(null=True, blank=True)

    # NOTE:
    # Regular game images are not to be stored in the repository due to their large size.
    # It is recommended to store them externally, for instance, on a dedicated server or a
    # BLOB (Binary Large Object) storage service such as AWS S3.
    image = models.TextField(default="/static/images/no_picture_available.png")

    # ================ GAMEPLAY INFORMATION ================
    rules = models.TextField(null=True, blank=True)

    min_players = models.PositiveIntegerField()
    max_players = models.PositiveIntegerField()
    suggested_age = models.PositiveSmallIntegerField(
        null=True, blank=True
    )  # Minimum recommendable age. For example, 8+ would be stored as 8.

    expected_playtime = models.PositiveIntegerField(null=True, blank=True)  # In Minutes
    min_playtime = models.PositiveIntegerField(null=True, blank=True)
    max_playtime = models.PositiveIntegerField(null=True, blank=True)

    complexity = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    categories = models.ManyToManyField("Category", related_name="games", blank=True)
    mechanics = models.ManyToManyField("Mechanic", related_name="games", blank=True)

    # ================ OTHER ================
    BGG_id = models.PositiveIntegerField(null=True, blank=True)  # BoardGameGeek ID

    # ================ VALIDATON ================
    def clean(self):
        # Ensures min_players is not greater than max_players
        if self.min_players and self.max_players and self.min_players > self.max_players:
            raise ValidationError({"min_players": "min_players cannot be greater than max_players"})

        # Validate playtime constraints for all combinations of min_playtime, max_playtime, and expected_playtime
        if self.min_playtime is not None and self.max_playtime is not None:
            if self.min_playtime > self.max_playtime:
                raise ValidationError({"min_playtime": "min_playtime cannot be greater than max_playtime"})

        if self.expected_playtime is not None:
            if self.min_playtime is not None and self.expected_playtime < self.min_playtime:
                raise ValidationError({"expected_playtime": "expected_playtime cannot be less than min_playtime"})

            if self.max_playtime is not None and self.expected_playtime > self.max_playtime:
                raise ValidationError({"expected_playtime": "expected_playtime cannot be greater than max_playtime"})

    def save(self, *args, **kwargs):
        # Calls full_clean to run all model validations, including the custom clean method and built-in field checks.
        # https://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model.full_clean
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Person(models.Model):
    """
    A person associated with a game, such as a designer or artist.
    This model is intended to track simple relationships between people and games.
    """

    DESIGNER = 1
    ARTIST = 2

    ROLE_CHOICES = (
        (DESIGNER, "Designer"),
        (ARTIST, "Artist"),
    )

    name = models.TextField()
    person_role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)
    games = models.ManyToManyField(Game, related_name="people")

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """
    A publisher of a game.
    """

    name = models.TextField()
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
    image = models.TextField(default="/static/images/no_picture_available.png")

    def __str__(self):
        return self.name


class Mechanic(models.Model):
    """
    Mechanic of the game like Dice Rolling, Hand Management, etc.
    See a full list of options: https://boardgamegeek.com/browse/boardgamemechanic
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    image = models.TextField(default="/static/images/no_picture_available.png")

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

    # ================ VALIDATON ================
    def clean(self):
        # Ensures min_players is not greater than max_players
        if self.min_players > self.max_players:
            raise ValidationError({"min_players": "min_players cannot be greater than max_players"})

    def save(self, *args, **kwargs):
        # Calls full_clean to run all validations before saving
        self.full_clean()
        super().save(*args, **kwargs)


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
    outcome = models.PositiveSmallIntegerField(choices=OUTCOMES, blank=True, null=True)
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
    matches = models.ManyToManyField(Match, related_name="matches", blank=True)
    winners = models.ManyToManyField(User, related_name="won_tournaments", blank=True)  # allow multiple winners
    num_winner = models.PositiveIntegerField(default=1)  # number of possible winners for the tournament
    players = models.ManyToManyField(User, related_name="joined_tournaments", blank=True)

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


class Announcement(models.Model):
    """
    An announcement, which can be sent to multiple users.
    """

    REMINDER = 2
    UPCOMING_MATCH = 3
    MATCH_PROPOSAL = 4

    ANNOUNCEMENT_TYPES = (
        (REMINDER, "REMINDER"),
        (UPCOMING_MATCH, "UPCOMING_MATCH"),
        (MATCH_PROPOSAL, "MATCH_PROPOSAL"),
    )

    recipients = models.ManyToManyField(User, related_name="announcements")
    content = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    type = models.PositiveIntegerField(choices=ANNOUNCEMENT_TYPES)

    def get_all_recipients(self):
        return self.recipients.all()

    def send_announcement(self):
        for recipient in self.get_all_recipients():
            notification = Notification.objects.create(
                receiver=recipient,
                message=self.content,
                type=self.type,
                actor_content_type=ContentType.objects.get_for_model(self.sender),
                actor_object_id=self.sender.pk,
            )
            notification.save()
        self.sent = True
        self.save()

    def is_announcement_sent(self):
        return self.sent

    def __str__(self) -> str:
        if self.is_announcement_sent():
            return (
                "Announcement sent to: "
                + "&".join([str(recipient) for recipient in self.get_all_recipients()])
                + ";\n content: "
                + self.content
            )
        else:
            return "Announcement not sent yet. Content is: " + self.content


class Chat(models.Model):
    """
    Represents the live chat feature for both players and spectators.
    It contains a list of messages, which are not mixed with the messages from
    other Chats. The messages are stored in the Message model.
    """

    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    # match: the match in which the chat is taking place.

    # visibility: a smallPositiveIntegerField representing the visibility of
    # the chat. This may be added later.

    def __str__(self):  # may be changed later
        return "Chat for match " + str(self.match)


class Message(models.Model):
    """
    Represents the individual message which populates one Chat entity. The
    messages from different Chats are not mixed together.
    """

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # timestamp of the
    # moment the message was created.
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Even if the user is deleted, the message will still exist such that the
    # message history is preserved. The sender field will be set to null.

    def __str__(self):  # may be changed later
        return "Message from " + str(self.sender) + ": " + self.content
