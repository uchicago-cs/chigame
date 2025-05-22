import copy

from django.db import models
from django.utils import timezone

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

    class Meta:
        unique_together = ("name", "game")

    def advance(self, user, amount=1):
        """
        Advance the progress of a user towards this achievement. This is separate from set_progress because
        we think developers will want to be able to call advance when the user does something that makes progress
        without having to figure out the current progress.
        """
        user_achievement, created = UserAchievement.objects.get_or_create(user=user, achievement=self)
        if created:
            amount -= 1
        if self.is_earned(user):
            return
        self.set_progress(user, user_achievement.progress + amount)

    def set_progress(self, user, progress, override=False):
        """
        Set the progress of a user toward an achievement.
        The "override" field allows achievements to be taken away from users, which we expect will be uncommon.
        """
        user_achievement, _ = UserAchievement.objects.get_or_create(user=user, achievement=self)
        if user_achievement.progress >= self.threshold - 1e-8 and not override:
            # Developers cannot take away achievements from users without specifying override
            return
        user_achievement.progress = progress
        if user_achievement.progress >= self.threshold - 1e-8:
            # Hardcoded subtraction accounts for float effects
            user_achievement.date_earned = timezone.now()
            user_achievement.last_updated = copy.copy(user_achievement.date_earned)
        else:
            user_achievement.date_earned = None
            user_achievement.last_updated = timezone.now()
        user_achievement.save(update_fields=["progress", "date_earned", "last_updated"])

    def is_earned(self, user):
        """
        Determines whether a given user has this achievement.
        For now, this is done by checking to make sure that there is a date_earned.
        """
        try:
            user_achievement = UserAchievement.objects.get(user=user, achievement=self)
            if user_achievement.date_earned is not None:
                return True
            return False
        except UserAchievement.DoesNotExist:
            return False


class UserAchievement(models.Model):
    """
    An Achievement that a User has earned from playing a game
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    pinned = models.BooleanField(default=False)
    date_earned = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(null=True, blank=True, default=1)
    # progress can be updated if achievement has a threshold

    def __str__(self):
        return f"{self.user} - {self.achievement}"

    class Meta:
        unique_together = ("user", "achievement")
