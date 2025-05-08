from django.db import models


class Region(models.Model):
    continent = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.region}, {self.country}"


class Game(models.Model):
    name = models.CharField(max_length=255)
    # other fields for Game as needed

    def __str__(self):
        return self.name


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    # other fields for User as needed

    def __str__(self):
        return self.username


class Leaderboard(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="leaderboards")

    def __str__(self):
        return self.name


class LeaderboardEntry(models.Model):
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name="entries")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leaderboard_entries")
    rank = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - Rank {self.rank}"


class Match(models.Model):
    # Define Match fields as needed
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match {self.id} on {self.date_played.date()}"


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="metric_scores")
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name="metric_scores")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="metric_scores")

    def __str__(self):
        return f"{self.user.username} - {self.metric.name}: {self.score}"
