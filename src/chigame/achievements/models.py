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

    class Meta:
        unique_together = ("name", "game")

    def advance(self, user, amount=1):
        """
        Advance the progress of a user towards this achievement.
        """
        user_achievement, created = UserAchievement.objects.get_or_create(user=user, achievement=self)
        if created:
            amount -= 1
        if user_achievement.progress >= self.threshold:
            return
        user_achievement.progress += amount
        if user_achievement.progress >= self.threshold:
            user_achievement.date_earned = models.DateTimeField(auto_now_add=True)
        user_achievement.save()


class UserAchievement(models.Model):
    """
    An Achievement that a User has earned from playing a game
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    pinned = models.BooleanField(default=False)
    date_earned = models.DateTimeField()
    progress = models.FloatField(null=True, blank=True, default=1)
    # progress can be updated as user makes progress on an achievement with a threshold

    class Meta:
        unique_together = ("user", "achievement")
