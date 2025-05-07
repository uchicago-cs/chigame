from django.db import models

from chigame.games.models import Game
from chigame.users.models import UserProfile


class Leaderboard(models.Model):
    pass
    # This is a placeholder for the Leaderboard model.


class LeaderboardPrivacySetting(models.Model):
    """
    Stores user Settings for leaderboard visibility.

    Setting hierarchy:
    1. Specific leaderboard Setting (highest priority)
    2. Game-level setting
    3. Global setting (lowest priority)
    """

    complete_opt_out = models.BooleanField(default=False)
    display_as_anonymous = models.BooleanField(default=False)

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ("user", "game", "leaderboard")

    def __str__(self):
        if self.leaderboard:
            return f"{self.user.display_name}'s settings for {self.leaderboard.name}"
        elif self.game:
            return f"{self.user.display_name}'s settings for {self.game.name}"
        else:
            return f"{self.user.display_name}'s global settings"

    @classmethod
    def get_user_setting(cls, user, game=None, leaderboard=None):
        """
        Retrieve the user's setting for a specific game or leaderboard.
        If no specific game or leaderboard is provided, return global setting.

        This follows the hierarchy:
        1. Specific leaderboard Setting (highest priority)
        2. Game-level setting
        3. Global setting (lowest priority)

        If no setting is found, return None.
        """
        if leaderboard:
            # specific leaderboard setting
            setting = cls.objects.filter(user=user, leaderboard=leaderboard).first()
            if setting:
                return setting
        if game:
            # game-level setting
            setting = cls.objects.filter(user=user, game=game, leaderboard__isnull=True).first()
            if setting:
                return setting
        else:
            # global setting
            setting = cls.objects.filter(user=user, game__isnull=True, leaderboard__isnull=True).first()
            if setting:
                return setting

        return None
