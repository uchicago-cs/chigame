from django.db import models
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from chigame.games.models import Game, Match
from chigame.leaderboards.serializers import LeaderboardEntrySerializer
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

    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.user.name} - Rank {self.rank}"


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
        return f"{self.user.user.name} - {self.metric.name}: {self.score}"


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
            return f"{self.user.user.name}'s settings for {self.leaderboard.name}"
        elif self.game:
            return f"{self.user.user.name}'s settings for {self.game.name}"
        else:
            return f"{self.user.user.name}'s global settings"

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

        # global setting
        setting = cls.objects.filter(user=user, game__isnull=True, leaderboard__isnull=True).first()
        if setting:
            return setting

        return None


class LeaderboardEntryListView(generics.ListAPIView):
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        game_id = self.kwargs["game_id"]
        region_filter = self.request.query_params.get("region")

        leaderboard = Game.objects.get(id=game_id).leaderboards.first()
        qs = LeaderboardEntry.objects.filter(leaderboard=leaderboard).select_related("user", "region")

        if region_filter:
            qs = qs.filter(region__region=region_filter)
        
        return qs.order_by("rank")

