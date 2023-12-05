import random

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from chigame.users.models import Group, Notification, User


class Game(models.Model):
    """
    A game like Chess, Checkers, Go, etc.
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

    The schedule of the tournament is as follows:
    1. Pre-tournament registration period, during which players can see the information of the tournament
    2. Registration period, during which players can register for the tournament
    3. Tournament, during which players play matches
    4. Post-tournament period, during which players can see the results of the tournament
    """

    name = models.CharField(max_length=255)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    registration_start_date = models.DateTimeField()  # the start date of the registration period
    registration_end_date = models.DateTimeField()  # the end date of the registration period
    tournament_start_date = models.DateTimeField()  # the start date of the tournament
    tournament_end_date = models.DateTimeField()  # the end date of the tournament
    max_players = models.PositiveIntegerField()
    description = models.TextField()  # not limited to 255 characters
    rules = models.TextField()  # not limited to 255 characters
    draw_rules = models.TextField()  # not limited to 255 characters
    num_winner = models.PositiveIntegerField(default=1)  # number of possible winners for the tournament
    archived = models.BooleanField(default=False)  # whether the tournament is archived by the admin

    matches = models.ManyToManyField(Match, related_name="tournament", blank=True)
    winners = models.ManyToManyField(User, related_name="won_tournaments", blank=True)  # allow multiple winners
    players = models.ManyToManyField(User, related_name="joined_tournaments", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_tournaments")

    @property
    def status(self):
        """
        Returns the status of the tournament.
        """
        if (
            self.registration_start_date > timezone.now()
        ):  # the period when the information of the tournament is displayed
            return "preparing"
        elif (
            self.registration_end_date > timezone.now()
        ):  # the registration period has started, users can register for the tournament
            return "registration open"
        elif (
            self.tournament_start_date > timezone.now()
        ):  # the period when the registration period has ended but the tournament has not started yet
            return "registration closed"
        elif self.tournament_end_date > timezone.now():  # the tournament has started, matches are being played
            return "tournament in progress"
        else:  # all matches have finished. The tournament has ended (any matches that have not finished are forfeited)
            return "tournament ended"

    def clean(self):  # restriction
        super().clean()  # call the parent class's clean() method

        # Section: players

        # the number of winners cannot be greater than the number of players, but can be equal to it
        if self.num_winner > self.max_players:
            raise ValidationError("The number of winners cannot be greater than the number of players.")

        # the number of winners should be greater than 0
        if self.num_winner <= 0:
            raise ValidationError("The number of winners should be greater than 0.")

        # the number of players should be less than or equal to the maximum number of players
        # Note: this is checked when the tournament is created and updated

        # the winners should also be players
        if self.pk is not None:  # the tournament is being updated
            for winner in self.winners.all():
                if winner not in self.players.all():
                    raise ValidationError("The winners should also be players.")

        # Section: dates

        # check if the dates are valid
        if self.registration_start_date is None:
            raise ValidationError("The registration start date is not valid.")
        if self.registration_end_date is None:
            raise ValidationError("The registration end date is not valid.")
        if self.tournament_start_date is None:
            raise ValidationError("The tournament start date is not valid.")
        if self.tournament_end_date is None:
            raise ValidationError("The tournament end date is not valid.")

        # all the dates should be in the future (the current time is not allowed)
        # when the tournament is created and would not be checked when the tournament is updated (
        # the date cannot be changed after the tournament is created)
        if self.pk is None:  # the tournament is being created
            if self.registration_start_date < timezone.now():
                raise ValidationError("The registration start date should be in the future.")
            if self.registration_end_date < timezone.now():
                raise ValidationError("The registration end date should be in the future.")
            if self.tournament_start_date < timezone.now():
                raise ValidationError("The tournament start date should be in the future.")
            if self.tournament_end_date < timezone.now():
                raise ValidationError("The tournament end date should be in the future.")

        # the registration start date should be earlier than the registration end date
        if self.registration_start_date >= self.registration_end_date:
            raise ValidationError("The registration start date should be earlier than the registration end date.")

        # the tournament start date should be earlier than the tournament end date
        if self.tournament_start_date >= self.tournament_end_date:
            raise ValidationError("The tournament start date should be earlier than the tournament end date.")

        # the registration end date should be earlier than the tournament start date
        if self.registration_end_date >= self.tournament_start_date:
            raise ValidationError("The registration end date should be earlier than the tournament start date.")

        # Section: archived

        # the tournament can only be archived if it has ended
        if self.archived and self.status != "tournament ended":
            raise ValidationError("The tournament can only be archived if it has ended.")

    def get_all_matches(self):
        return self.matches.all()

    def get_all_winners(self):
        return self.winners.all()

    def get_all_players(self):
        return self.players.all()

    def set_archive(self, archive):
        """
        Sets the archive field of the tournament. The tournament can only be archived if it has ended.
        """
        if not isinstance(archive, bool):
            raise TypeError("The archive field should be a boolean.")

        # the tournament can only be archived if it has ended
        if self.status != "tournament ended":
            raise ValidationError("The tournament can only be archived if it has ended.")

        self.archived = archive
        self.save()

    def check_and_end_tournament(self):
        """
        Checks if the tournament end date has reached and ends the tournament if it has.
        Any matches that have not finished are forfeited.
        """
        if self.status == "tournament ended":
            brackets = self.matches.all()
            for bracket in brackets:
                assert isinstance(bracket, Match)
                bracket_users = bracket.players.all()
                bracket_players = [Player.objects.get(user=user, match=bracket) for user in bracket_users]
                bracket_with_outcome = any(player.outcome is not None for player in bracket_players)
                if not bracket_with_outcome:  # the match has not finished
                    for player in bracket_players:
                        player.outcome = Player.WITHDRAWAL  # forfeit
                        player.save()
            self.end_tournament()

    def __str__(self):  # may be changed later
        return (
            "Tournament "
            + self.name
            + ": "
            + self.game.name
            + " from "
            + self.tournament_start_date.strftime("%m/%d/%Y")
            + " to "
            + self.tournament_end_date.strftime("%m/%d/%Y")
        )

    def create_tournaments_brackets(self) -> list[Match]:
        """
        Creates a list of brackets for the tournaments.

        Returns:
            a list of matches
        """
        players = [player for player in self.players.all()]  # the players in the tournament
        brackets = []
        random.shuffle(players)  # shuffle the players
        # Create a list of brackets (match assignment) for the tournament
        for i in range(0, len(players), self.game.max_players):
            game = self.game
            lobby = Lobby.objects.create(
                match_status=Lobby.Lobbied,
                name=self.name + " " + str(i),
                game=game,
                game_mod_status=Lobby.Default_game,
                created_by=players[i],
                min_players=game.min_players,
                max_players=game.max_players,
            )
            lobby.members.set(players[i : i + self.game.max_players])
            lobby.save()
            players_in_match = players[i : i + self.game.max_players]
            match = Match.objects.create(game=game, lobby=lobby, date_played=self.tournament_start_date)
            # date_played is set to the start date of the tournament for now
            match.players.set(players_in_match)
            match.save()
            brackets.append(match)

            self.matches.add(match)

        return brackets

    def next_round_tournaments_brackets(self) -> list[Match]:
        """
        Creates a list of brackets for the next round of the tournaments.

        Returns:
            a list of matches
        """
        brackets = self.matches.all()  # the matches of the previous round
        players = []

        # get the winners of the previous round
        for bracket in brackets:
            assert isinstance(bracket, Match)
            bracket_users = bracket.players.all()
            bracket_players = [Player.objects.get(user=user, match=bracket) for user in bracket_users]
            bracket_winners = [
                player for player in bracket_players if player.outcome == Player.WIN
            ]  # allow multiple winners
            # currently only players who win instead of draw can advance to the next round
            for winner in bracket_winners:
                players.append(winner.user)

        # check if the number of players is small enough to end the tournament
        if len(players) <= self.num_winner:
            self.end_tournament()
            return []  # the tournament is finished

        # clear the matches of the previous round
        self.matches.clear()

        # create the matches of the next round
        random.shuffle(players)
        next_round_brackets = []
        # Create a list of brackets (match assignment) for the tournament
        for i in range(0, len(brackets), self.game.max_players):
            game = self.game
            lobby = Lobby.objects.create(
                match_status=Lobby.Lobbied,
                name=self.name + " " + str(i),
                game=game,
                game_mod_status=Lobby.Default_game,
                created_by=brackets[i].winners.all()[0],
                min_players=game.min_players,
                max_players=game.max_players,
            )
            lobby.members.set(players[i : i + self.game.max_players])
            lobby.save()
            players_in_match = players[i : i + self.game.max_players]
            match = Match.objects.create(game=game, lobby=lobby, date_played=self.tournament_start_date)
            match.players.set(players_in_match)
            match.save()
            next_round_brackets.append(match)

            self.matches.add(match)

        return next_round_brackets

    def end_tournament(self) -> None:
        """
        Ends the tournament.

        Returns:
            None
        """

        winners = []
        brackets = self.matches.all()
        for bracket in brackets:  # the matches of the previous round
            # get the winners of the previous round
            assert isinstance(bracket, Match)
            bracket_users = bracket.players.all()
            bracket_players = [Player.objects.get(user=user, match=bracket) for user in bracket_users]
            bracket_winners = [
                player.user for player in bracket_players if player.outcome == Player.WIN
            ]  # allow multiple winners
            # currently only players who win instead of draw can advance to the next round
            for winner in bracket_winners:
                winners.append(winner)

        self.winners.set(winners)
        self.matches.clear()
        self.save()

        # Note: we don't delete the tournament because we want to keep it in the database

    def tournament_sign_up(self, user: User) -> int:
        """
        Signs up a user for a tournament. If the user has already joined the
        tournament, nothing happens.

        Args:
            user: the user

        Returns:
            int: 0 if the user has successfully signed up for the tournament,
            1 if the user has already joined the tournament,
            2 if the tournament is full,
            3 if the registration period of tournament has already ended
        """
        if self.status != "registration open":
            # The registration period has ended (the join and withdraw buttons only appear
            # during the registration period)
            return 3
        if user in self.players.all():
            # The user has already joined the tournament
            return 1
        if self.players.count() >= self.max_players:
            # The tournament is full
            return 2
        self.players.add(user)
        self.save()
        return 0

    def tournament_withdraw(
        self,
        user: User,
    ) -> int:
        """
        Withdraws a user from a tournament. If the user has not joined the
        tournament, nothing happens.

        Args:
            user: the user

        Returns:
            int: 0 if the user has successfully withdrawn from the tournament,
            1 if the user has not joined the tournament
            3 if the registration period of tournament has already ended
        """
        if self.status != "registration open":
            # The registration period has ended (the join and withdraw buttons only appear
            # during the registration period)
            return 3
        if user not in self.players.all():
            # The user has not joined the tournament
            return 1
        self.players.remove(user)
        self.save()
        return 0


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

    tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return "Chat for tournament " + str(self.tournament)


class Message(models.Model):
    """
    Represents the individual message which populates one Chat entity. The
    messages from different Chats are not mixed together.
    """

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    token_id = models.PositiveIntegerField(default=None)
    update_on = models.PositiveIntegerField(default=None, null=True)

    def save(self, *args, **kwargs):
        if not self.token_id:
            last_message = Message.objects.filter(chat=self.chat).order_by("-token_id").first()
            self.token_id = last_message.token_id + 1 if last_message else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Message from " + str(self.sender) + ": " + self.content


class Review(models.Model):
    "Represents a game review"
    title = models.TextField(blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # the ratings will range from 1-5 with one being a low rating and 5 being a high rating
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} by {self.user} for {self.game}: {self.review}"

    def clean(self):
        if (self.review == "" and self.rating is None) or (self.rating == "" and self.review is None):
            raise ValidationError("At least one of 'review' or 'rating' must be provided.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
