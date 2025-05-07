from django.db import models

from chigame.games.models import Game
from chigame.users.models import UserProfile


class Leaderboard(models.Model):
    pass
    # This is a placeholder for the Leaderboard model.


class LeaderboardPrivacySetting(models.Model):
    """
    Stores user preferences for leaderboard visibility.

    Preference hierarchy:
    1. Specific leaderboard preference (highest priority)
    2. Game-level preference
    3. Global preference (lowest priority)
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
            return f"{self.user.display_name}'s preferences for {self.leaderboard.name}"
        elif self.game:
            return f"{self.user.display_name}'s preferences for {self.game.name}"
        else:
            return f"{self.user.display_name}'s global preferences"

    @classmethod
    def get_user_preferences(cls, user, game=None, leaderboard=None):
        """
        Retrieve the user's preferences for a specific game or leaderboard.
        If no specific game or leaderboard is provided, return global preferences.
        """
        if leaderboard:
            # specific leaderboard preference
            return cls.objects.filter(user=user, leaderboard=leaderboard).first()
        elif game:
            # game-level preference
            return cls.objects.filter(user=user, game=game, leaderboard__isnull=True).first()
        else:
            # global preference
            return cls.objects.filter(user=user, game__isnull=True, leaderboard__isnull=True).first()
