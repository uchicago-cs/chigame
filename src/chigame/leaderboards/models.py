from django.db import models

from chigame.games.models import Game, Match
from chigame.users.models import UserProfile


class Region(models.Model):
    continent = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.region}, {self.country}"


class Leaderboard(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="leaderboards")

    def __str__(self):
        return self.name


class LeaderboardEntry(models.Model):
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name="entries")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="leaderboard_entries")
    rank = models.IntegerField()

    def __str__(self):
        return f"{self.user.display_name} - Rank {self.rank}"


class Metric(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="metrics")

    def __str__(self):
        return self.name


class MetricScore(models.Model):
    score = models.IntegerField()
    leaderboard_entry = models.ForeignKey(LeaderboardEntry, on_delete=models.CASCADE, related_name="metric_scores")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="metric_scores")
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name="metric_scores")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="metric_scores")

    def __str__(self):
        return f"{self.user.display_name} - {self.metric.name}: {self.score}"
