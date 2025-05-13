import datetime
from django.test import TestCase
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

# Import factory definitions for model instantiation
from .factories import (
    AuthUserFactory,
    UserProfileFactory,
    RegionFactory,
    GameFactory,
    LobbyFactory,
    MatchFactory,
    LeaderboardFactory,
    LeaderboardEntryFactory,
    MetricFactory,
    MetricScoreFactory,
)

# Core application models under test
from chigame.games.models import Game, Lobby, Match
from chigame.users.models import UserProfile
from chigame.leaderboards.models import (
    Region,
    Leaderboard,
    LeaderboardEntry,
    Metric,
    MetricScore,
)

# Ensure display_name property exists for UserProfile __str__ tests
UserProfile.display_name = property(lambda self: self.user.username)
AuthUser = get_user_model()


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create sample instances for all models using factories
        cls.region = RegionFactory()
        cls.auth_user = AuthUserFactory()
        cls.user_profile = UserProfileFactory(user=cls.auth_user)
        cls.game = GameFactory()
        cls.lobby = LobbyFactory(game=cls.game, created_by=cls.auth_user)
        cls.match = MatchFactory(game=cls.game, lobby=cls.lobby)
        cls.leaderboard = LeaderboardFactory(game=cls.game)
        cls.entry = LeaderboardEntryFactory(
            leaderboard=cls.leaderboard,
            user=cls.user_profile,
        )
        cls.metric = MetricFactory(game=cls.game)
        cls.metric_score = MetricScoreFactory(
            leaderboard_entry=cls.entry,
            user=cls.user_profile,
            metric=cls.metric,
            match=cls.match,
        )

    # String representation tests
    def test_region_str(self):
        self.assertEqual(str(self.region), f"{self.region.region}, {self.region.country}")

    def test_auth_user_str(self):
        self.assertEqual(str(self.auth_user), self.auth_user.email)

    def test_user_profile_str(self):
        expected = f"UserProfile object ({self.user_profile.id})"
        self.assertEqual(str(self.user_profile), expected)

    def test_game_str(self):
        self.assertEqual(str(self.game), self.game.name)

    def test_lobby_str(self):
        expected = f"Lobby object ({self.lobby.id})"
        self.assertEqual(str(self.lobby), expected)

    def test_match_str(self):
        match = Match.objects.get(id=self.match.id)
        expected = f"Match object ({match.id})"
        self.assertEqual(str(match), expected)

    def test_leaderboard_str(self):
        self.assertEqual(str(self.leaderboard), self.leaderboard.name)

    def test_entry_str(self):
        expected = f"{self.user_profile.user.username} - Rank {self.entry.rank}"
        self.assertEqual(str(self.entry), expected)

    def test_metric_str(self):
        self.assertEqual(str(self.metric), self.metric.name)

    def test_metric_score_str(self):
        expected = f"{self.user_profile.user.username} - {self.metric.name}: {self.metric_score.score}"
        self.assertEqual(str(self.metric_score), expected)

    # Validation tests for required fields on models
    def test_game_required_fields(self):
        incomplete = Game(name="Incomplete Game")
        with self.assertRaises(ValidationError):
            incomplete.full_clean()
        partial = Game(name="Test Game 2", description="desc only", min_players=1)
        with self.assertRaises(ValidationError):
            partial.full_clean()

    def test_lobby_required_fields(self):
        no_game = Lobby(name="No Game", created_by=self.auth_user, min_players=1, max_players=2)
        with self.assertRaises(ValidationError):
            no_game.full_clean()
        no_creator = Lobby(name="No Creator", game=self.game, min_players=1, max_players=2)
        with self.assertRaises(ValidationError):
            no_creator.full_clean()

    # Integrity tests for non-null constraints on Match
    def test_match_required_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Match.objects.create(lobby=self.lobby, date_played=timezone.now())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Match.objects.create(game=self.game, date_played=timezone.now())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Match.objects.create(game=self.game, lobby=self.lobby)

        # Remove original to avoid unique constraint conflict, then verify valid creation
        self.match.delete()
        temp = Match.objects.create(game=self.game, lobby=self.lobby, date_played=timezone.now())
        self.assertIsNotNone(temp.pk)
        temp.delete()

    # Tests for blank description allowance
    def test_blank_description_fields_leaderboard_metric(self):
        lb2 = LeaderboardFactory(game=self.game, description="")
        self.assertEqual(lb2.description, "")
        m2 = MetricFactory(game=self.game, description="")
        self.assertEqual(m2.description, "")

    # Auto-timestamp behavior test
    def test_match_date_played_auto_now_add(self):
        self.assertIsInstance(self.match.date_played, datetime.datetime)
        self.assertTrue(timezone.now() - self.match.date_played < datetime.timedelta(seconds=5))

    # Cascade delete behavior tests
    def test_cascade_delete_game(self):
        tmp = AuthUserFactory()
        g = GameFactory()
        l = LobbyFactory(game=g, created_by=tmp)
        m = MatchFactory(game=g, lobby=l)
        gid, lid, mid = g.id, l.id, m.id
        g.delete()
        self.assertFalse(Game.objects.filter(id=gid).exists())
        self.assertFalse(Lobby.objects.filter(id=lid).exists())
        self.assertFalse(Match.objects.filter(id=mid).exists())

    def test_cascade_delete_lobby(self):
        tmp = AuthUserFactory()
        g = GameFactory()
        l = LobbyFactory(game=g, created_by=tmp)
        m = MatchFactory(game=g, lobby=l)
        lid, mid = l.id, m.id
        l.delete()
        self.assertFalse(Lobby.objects.filter(id=lid).exists())
        self.assertFalse(Match.objects.filter(id=mid).exists())

    def test_cascade_delete_leaderboard(self):
        lb = LeaderboardFactory(game=self.game)
        tmp = AuthUserFactory()
        prof = UserProfileFactory(user=tmp)
        entry = LeaderboardEntryFactory(leaderboard=lb, user=prof)
        eid = entry.id
        lb.delete()
        self.assertFalse(LeaderboardEntry.objects.filter(id=eid).exists())

    def test_cascade_delete_user_profile_to_metric_scores(self):
        tmp = AuthUserFactory()
        prof = UserProfileFactory(user=tmp)
        entry = LeaderboardEntryFactory(leaderboard=self.leaderboard, user=prof)
        ms = MetricScoreFactory(
            leaderboard_entry=entry,
            user=prof,
            metric=self.metric,
            match=self.match,
        )
        pid, eid, mid = prof.id, entry.id, ms.id
        prof.delete()
        self.assertFalse(UserProfile.objects.filter(id=pid).exists())
        self.assertFalse(LeaderboardEntry.objects.filter(id=eid).exists())
        self.assertFalse(MetricScore.objects.filter(id=mid).exists())

    def test_cascade_delete_auth_user_to_user_profile(self):
        tmp = AuthUserFactory()
        prof = UserProfileFactory(user=tmp)
        pid = prof.id
        tmp.delete()
        self.assertFalse(UserProfile.objects.filter(id=pid).exists())

    # Verification of related_name and reverse relationships
    def test_related_name_access(self):
        auth_user = AuthUser.objects.get(pk=self.auth_user.pk)
        profile = UserProfile.objects.get(pk=self.user_profile.pk)
        game = Game.objects.get(pk=self.game.pk)
        lobby = Lobby.objects.get(pk=self.lobby.pk)
        match_inst = Match.objects.get(pk=self.match.pk)
        leaderboard = Leaderboard.objects.get(pk=self.leaderboard.pk)
        entry = LeaderboardEntry.objects.get(pk=self.entry.pk)
        metric = Metric.objects.get(pk=self.metric.pk)
        ms = MetricScore.objects.get(pk=self.metric_score.pk)

        self.assertIn(leaderboard, game.leaderboards.all())
        self.assertIn(lobby, game.lobby_set.all())
        self.assertIn(match_inst, game.match_set.all())
        self.assertIn(match_inst, Match.objects.filter(lobby_id=lobby.id))
        self.assertEqual(lobby.created_by, auth_user)
        self.assertEqual(lobby.min_players, game.min_players)
        self.assertEqual(lobby.max_players, game.max_players)
        self.assertIn(entry, profile.leaderboard_entries.all())
        self.assertIn(ms, profile.metric_scores.all())
        self.assertEqual(auth_user.userprofile, profile)
        self.assertIn(lobby, auth_user.lobby_set.all())
        self.assertIn(entry, leaderboard.entries.all())
        self.assertIn(ms, entry.metric_scores.all())
        self.assertIn(ms, metric.metric_scores.all())
        self.assertIn(ms, match_inst.metric_scores.all())

    # Creation tests for all model fields
    def test_user_profile_creation_all_fields(self):
        tmp = AuthUserFactory()
        prof = UserProfileFactory(user=tmp, bio="A test bio.")
        self.assertEqual(prof.user_id, tmp.id)
        self.assertEqual(prof.bio, "A test bio.")
        self.assertIsNotNone(prof.date_joined)

    def test_game_creation_all_fields(self):
        g2 = GameFactory(name="FullGame", description="desc", min_players=2, max_players=4, complexity=3)
        self.assertEqual(g2.name, "FullGame")
        self.assertEqual(g2.description, "desc")
        self.assertEqual(g2.min_players, 2)
        self.assertEqual(g2.max_players, 4)
        self.assertEqual(g2.complexity, 3)

    def test_lobby_creation_all_fields(self):
        tmp = AuthUserFactory()
        g3 = GameFactory()
        l3 = LobbyFactory(game=g3, created_by=tmp)
        self.assertEqual(l3.game, g3)
        self.assertEqual(l3.created_by, tmp)
        self.assertEqual(l3.min_players, g3.min_players)
        self.assertEqual(l3.max_players, g3.max_players)

    def test_match_creation_all_fields(self):
        tmp = AuthUserFactory()
        g4 = GameFactory()
        l4 = LobbyFactory(game=g4, created_by=tmp)
        m4 = MatchFactory(game=g4, lobby=l4)
        self.assertEqual(m4.game, g4)
        self.assertEqual(m4.lobby, l4)
        self.assertTrue(timezone.now() - m4.date_played < datetime.timedelta(seconds=5))

    def test_metric_score_creation_all_fields(self):
        ms = MetricScore.objects.get(id=self.metric_score.id)
        self.assertEqual(ms.score, self.metric_score.score)
        self.assertEqual(ms.leaderboard_entry_id, self.entry.id)
        self.assertEqual(ms.user_id, self.user_profile.id)
        self.assertEqual(ms.metric_id, self.metric.id)
        self.assertEqual(ms.match_id, self.match.id)
