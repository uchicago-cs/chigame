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


class Notification(models.Model):
    """
    A notification, which can be sent to multiple users.
    """

    recipients = models.ManyToManyField(User, related_name="notifications")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # visibility: a smallPositiveIntegerField representing the visibility of
    # the notification. This may be added later.

    def get_all_recipients(self):
        return self.recipients.all()

    def __str__(self):  # may be changed later
        recipients_str = "&".join([str(recipient) for recipient in self.get_all_recipients()])
        return "Notification sent to: " + recipients_str + ";\n content: " + self.content


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
