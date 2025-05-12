import datetime

from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone

from chigame.leaderboards.models import (
    Region, Game, User, Leaderboard,
    LeaderboardEntry, Match, Metric, MetricScore
)


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # ---- One-time setup for all tests ----
        cls.region = Region.objects.create(
            continent="North America",
            country="USA",
            region="Midwest"
        )
        cls.user = User.objects.create(
            username="testuser",
            region=cls.region
        )
        cls.game = Game.objects.create(name="Test Game")
        cls.leaderboard = Leaderboard.objects.create(
            name="Test LB",
            description="Test game",
            game=cls.game
        )
        cls.entry = LeaderboardEntry.objects.create(
            leaderboard=cls.leaderboard,
            user=cls.user,
            rank=1
        )
        cls.metric = Metric.objects.create(
            name="Wins",
            unit="wins",
            description="Total wins",
            game=cls.game
        )
        cls.match = Match.objects.create()
        cls.metric_score = MetricScore.objects.create(
            score=10,
            leaderboard_entry=cls.entry,
            user=cls.user,
            metric=cls.metric,
            match=cls.match
        )

    # ---- __str__ Method Tests ----

    def test_region_str(self):
        self.assertEqual(str(self.region), "Midwest, USA")

    def test_game_str(self):
        # Game.__str__ returns its name
        self.assertEqual(str(self.game), "Test Game")

    def test_user_str(self):
        self.assertEqual(str(self.user), "testuser")

    def test_leaderboard_str(self):
        self.assertEqual(str(self.leaderboard), "Test LB")

    def test_entry_str(self):
        self.assertEqual(str(self.entry), "testuser - Rank 1")

    def test_match_str(self):
        # Fetch again to ensure date_played is set
        match = Match.objects.get(id=self.match.id)
        expected = f"Match {match.id} on {match.date_played.date()}"
        self.assertEqual(str(match), expected)

    def test_metric_str(self):
        self.assertEqual(str(self.metric), "Wins")

    def test_metric_score_str(self):
        self.assertEqual(str(self.metric_score), "testuser - Wins: 10")

    # ---- Field Constraint Tests ----

    def test_user_username_unique(self):
        # Enforce unique username constraint
        with self.assertRaises(IntegrityError):
            User.objects.create(username="testuser")

    def test_user_can_have_null_region(self):
        # region is nullable
        user2 = User.objects.create(username="noregion")
        self.assertIsNone(user2.region)
        self.assertEqual(str(user2), "noregion")

    def test_blank_description_fields(self):
        # description on Leaderboard and Metric may be blank
        lb2 = Leaderboard.objects.create(
            name="LB2", description="", game=self.game
        )
        self.assertEqual(lb2.description, "")

        m2 = Metric.objects.create(
            name="M2", unit="units", description="", game=self.game
        )
        self.assertEqual(m2.description, "")

    def test_match_date_played_auto_now_add(self):
        # date_played is auto-set and recent
        self.assertIsInstance(self.match.date_played, datetime.datetime)
        self.assertTrue(
            timezone.now() - self.match.date_played < datetime.timedelta(seconds=5)
        )

    # ---- Cascade / SET_NULL Behavior Tests ----

    def test_cascade_delete_game(self):
        # Deleting a Game should delete its Leaderboards and Metrics
        game2 = Game.objects.create(name="TempGame")
        lb2 = Leaderboard.objects.create(name="TempLB", game=game2)
        metric2 = Metric.objects.create(name="TempMetric", unit="u", game=game2)

        game2.delete()
        self.assertFalse(Leaderboard.objects.filter(id=lb2.id).exists())
        self.assertFalse(Metric.objects.filter(id=metric2.id).exists())

    def test_cascade_delete_leaderboard(self):
        # Deleting a Leaderboard should delete its LeaderboardEntries
        lb3 = Leaderboard.objects.create(name="LB3", game=self.game)
        entry3 = LeaderboardEntry.objects.create(
            leaderboard=lb3, user=self.user, rank=5
        )

        lb3.delete()
        self.assertFalse(LeaderboardEntry.objects.filter(id=entry3.id).exists())

    def test_cascade_delete_user_metric_scores(self):
        # Deleting a User should delete their MetricScores (via cascade)
        ms_id = self.metric_score.id
        self.user.delete()
        self.assertFalse(MetricScore.objects.filter(id=ms_id).exists())

    def test_user_region_set_null_on_region_delete(self):
        # Deleting a Region should set User.region to None
        region_id = self.region.id
        Region.objects.filter(id=region_id).delete()
        self.user.refresh_from_db()
        self.assertIsNone(self.user.region)

    # ---- Related Name Access Tests ----

    def test_related_name_access(self):
        # Verify reverse lookups via related_name
        self.assertIn(self.leaderboard, self.game.leaderboards.all())
        self.assertIn(self.entry, self.user.leaderboard_entries.all())
        self.assertIn(self.entry, self.leaderboard.entries.all())
        self.assertIn(self.metric_score, self.entry.metric_scores.all())
        self.assertIn(self.metric_score, self.user.metric_scores.all())
        self.assertIn(self.metric_score, self.metric.metric_scores.all())
        self.assertIn(self.metric_score, self.match.metric_scores.all())

    # ---- Full-field Creation Tests ----

    def test_region_creation_all_fields(self):
        region2 = Region.objects.create(
            continent="Asia", country="Japan", region="Kanto"
        )
        self.assertEqual(region2.continent, "Asia")
        self.assertEqual(region2.country, "Japan")
        self.assertEqual(region2.region, "Kanto")

    def test_metric_score_creation_all_fields(self):
        # Verify MetricScore fields saved correctly
        ms = MetricScore.objects.get(id=self.metric_score.id)
        self.assertEqual(ms.score, 10)
        self.assertEqual(ms.leaderboard_entry_id, self.entry.id)
        self.assertEqual(ms.user_id, self.user.id)
        self.assertEqual(ms.metric_id, self.metric.id)
        self.assertEqual(ms.match_id, self.match.id)
