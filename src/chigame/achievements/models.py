from django.db import models

from chigame.games.models import Game
from chigame.users.models import User


class Achievement(models.Model):
    """
    An award or acknowledgement offered by a game.
    """

    class Rarity(models.IntegerChoices):
        COMMON = 1, "Common"
        UNCOMMON = 2, "Uncommon"
        RARE = 3, "Rare"
        PRECIOUS = 4, "Precious"

    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    spoiler = models.BooleanField(default=False)
    rarity = models.IntegerField(choices=Rarity.choices)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    threshold = models.FloatField(null=True, blank=True, default=1)
    # threshold is amount needed to earn achievement (e.g. 5.0 wins)

    def __str__(self):
        return f"{self.name} ({self.game})"

    def get_user_achievement(self, user):
        """
        Method of an achievement that, given a user, returns the UserAchievement object
        associated with that achievement and user. If no such object exists, returns None.
        """
        try:
            user_achievement = UserAchievement.objects.get(achievement=self, user=user)
            return user_achievement
        except UserAchievement.DoesNotExist:
            return None

    def get_achievement_percentage(self):
        """
        Method of achievement that returns as a float the percentage of the associated game's
        users who have gotten that achievement
        """
        users = self.game.users.all()
        obtained = 0
        for user in users:
            user_achievement = self.get_user_achievement(user)
            if user_achievement is not None and user_achievement.date_earned is not None:
                obtained += 1
        return obtained / len(users)

    class Meta:
        unique_together = ("name", "game")


class UserAchievement(models.Model):
    """
    An Achievement that a User has earned from playing a game
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    pinned = models.BooleanField(default=False)
    date_earned = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    progress = models.FloatField(null=True, blank=True, default=1)
    # progress can be updated if achievement has a threshold

    def __str__(self):
        return f"{self.user} - {self.achievement}"

    class Meta:
        unique_together = ("user", "achievement")
