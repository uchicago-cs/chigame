from django.db import models

from chigame.games.models import Game, Match
from chigame.users.models import User


class UserGameStat(models.Model):
    """
    for tracking an individual user's overall progress within a game (not specific to achievements)
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    join_date = models.DateTimeField(auto_now_add=True)  # when user first played game. maybe auto?
    streak_start = models.DateTimeField()  # start of user's current streak; could be today (no streak)

    class Meta:
        unique_together = ["user", "game"]


class Achievement(models.Model):
    """
    An award or acknowledgement offered by a game. The multi_player_only field
    is set to True if the achievement can only be earned through co-op play in a
    game that also has a single-player option
    """

    class Rarity(models.IntegerChoices):
        COMMON = 1, "Common"
        UNCOMMON = 2, "Uncommon"
        RARE = 3, "Rare"
        PRECIOUS = 4, "Precious"

    name = models.TextField()
    api_name = models.TextField(unique=True)  # some sort of external id that connects achievements to Games thru api
    description = models.TextField(null=True, blank=True)
    spoiler = models.BooleanField(default=False)
    rarity = models.IntegerField(choices=Rarity.choices)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    multi_player_only = models.BooleanField(default=False)  # new
    threshold = models.IntegerField(null=True, blank=True)  # amounted needed to earn achievement (e.g. 5 wins)


class UserAchievementStat(models.Model):
    """
    tracks a user's progress towards a progress-based achievement
    """

    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)  # links to Achievement stat_name
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    progress = models.IntegerField(null=True, blank=True)
    # can auto create a UserAchievment once progress reaches Achievement threshold

    class Meta:
        unique_together = ["achievement", "user"]


class UserAchievement(models.Model):
    """
    An Achievement that a User has earned from playing a game
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    match = models.ForeignKey(
        Match, null=True, blank=True, on_delete=models.CASCADE
    )  # match to reference to find teammates for a multiplayer achievement?
    pinned = models.BooleanField(default=False)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")


class GameOverallStat(models.Model):
    """
    for tracking overall progress/stats for a game; not for individual users
    """

    game = models.ForeignKey(Game, unique=True, on_delete=models.CASCADE)
    players = models.IntegerField()  # number of users who have played game 1+ times (can update a match ends)
    rating = models.FloatField()  # average of user ratings


class GameAchievementStat(models.Model):
    """
    for tracking overall achievement progress within a game; mainly number of
    users who have earned a particular achievement
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    num_players = models.IntegerField()  # number of players who have earned this achievement

    class Meta:
        unique_together = ("game", "achievement")
