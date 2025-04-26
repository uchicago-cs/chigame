from django.db import models
from chigame.games.models import Game
from chigame.users.models import User


class Achievement(models.Model):
    """
    An award or acknowledgement offered by a game
    """
    class Rarity(models.IntegerChoices):
        COMMON = 1, 'Common'
        UNCOMMON = 2, 'Uncommon'
        RARE = 3, 'Rare'
        PRECIOUS = 4, 'Precious'
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    spoiler = models.BooleanField()
    rarity = models.IntegerField(choices=Rarity.choices)
    game = models.ForeignKey(Game, on_delete = models.CASCADE)

class UserAchievement(models.Model):
    """
    An Achievement that a User has earned from playing a game
    """
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete = models.CASCADE)
    pinned = models.BooleanField()
    date_earned = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'achievement')
