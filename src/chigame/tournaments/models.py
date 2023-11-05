from django.db import models
from django.urls import reverse

from chigame.games.models import Game, Match
from chigame.users.models import User


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

    def __str__(self):
        return (
            "Tournament "
            + self.name
            + ": "
            + self.game.name
            + "from "
            + self.start_date.strftime("%m/%d/%Y")
            + " to "
            + self.end_date.strftime("%m/%d/%Y")
        )

    def get_absolute_url(self):
        return reverse("tournaments:detail", kwargs={"pk": self.id})


class Notification(models.Model):
    """
    A notification, which can be sent to multiple users.
    """

    users = models.ManyToManyField(User, related_name="notifications")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # visibility: a smallPositiveIntegerField representing the visibility of the
    # notification. This may be added later.

    def __str__(self):
        return "Notification sent to " + self.users + "; content: " + self.content


class Chat(models.Model):
    """
    Represents the live chat feature for both players and spectators.
    It contains a list of messages, which are not mixed with the messages from
    other Chats.
    """

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    # match: the match in which the chat is taking place.

    # visibility: a smallPositiveIntegerField representing the visibility of
    # the chat. This may be added later.

    def __str__(self):
        return "Chat for match " + self.match


class Message(models.Model):
    """
    Represents the individual message which populates one Chat entity. The
    messages from different Chats are not mixed together.
    """

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # timestamp of the
    # moment the message was created.
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # Even if the user is deleted, the message
    # will still exist.

    def __str__(self):
        return "Message from " + self.sender + ": " + self.content
