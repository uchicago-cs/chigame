import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

# Core application models under test
from chigame.games.models import Game, Lobby, Match
from chigame.leaderboards.models import Leaderboard, LeaderboardEntry, LeaderboardPrivacySetting, Metric, MetricScore
from chigame.users.models import UserProfile

# Import factory definitions for model instantiation
from .factories import (
    AuthUserFactory,
    GameFactory,
    GamePrivacySettingFactory,
    GlobalPrivacySettingFactory,
    LeaderboardEntryFactory,
    LeaderboardFactory,
    LeaderboardSpecificPrivacySettingFactory,
    LobbyFactory,
    MatchFactory,
    MetricFactory,
    MetricScoreFactory,
    RegionFactory,
    UserProfileFactory,
)

AuthUser = get_user_model()


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Instantiate one of each model via factories
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

    # String-representation tests
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
        expected = f"{self.user_profile.user.name} - Rank {self.entry.rank}"
        self.assertEqual(str(self.entry), expected)

    def test_metric_str(self):
        self.assertEqual(str(self.metric), self.metric.name)

    def test_metric_score_str(self):
        expected = f"{self.user_profile.user.name} - {self.metric.name}: {self.metric_score.score}"
        self.assertEqual(str(self.metric_score), expected)

    # Validation of required fields via full_clean()
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

    # Integrity tests for non-null constraints on the Match model
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

        # Remove original match to avoid unique conflicts, then verify valid creation
        self.match.delete()
        temp_match = Match.objects.create(game=self.game, lobby=self.lobby, date_played=timezone.now())
        self.assertIsNotNone(temp_match.pk)
        temp_match.delete()

    # Allow blank descriptions on Leaderboard and Metric
    def test_blank_description_fields_leaderboard_metric(self):
        lb2 = LeaderboardFactory(game=self.game, description="")
        self.assertEqual(lb2.description, "")
        m2 = MetricFactory(game=self.game, description="")
        self.assertEqual(m2.description, "")

    # Test that date_played is auto-added and recent
    def test_match_date_played_auto_now_add(self):
        self.assertIsInstance(self.match.date_played, datetime.datetime)
        delta = timezone.now() - self.match.date_played
        self.assertTrue(delta < datetime.timedelta(seconds=5))

    # Cascade-delete behavior when Game is deleted
    def test_cascade_delete_game(self):
        tmp_user = AuthUserFactory()
        game = GameFactory()
        lobby = LobbyFactory(game=game, created_by=tmp_user)
        match = MatchFactory(game=game, lobby=lobby)
        gid, lid, mid = game.id, lobby.id, match.id
        game.delete()
        self.assertFalse(Game.objects.filter(id=gid).exists())
        self.assertFalse(Lobby.objects.filter(id=lid).exists())
        self.assertFalse(Match.objects.filter(id=mid).exists())

    # Cascade-delete behavior when Lobby is deleted
    def test_cascade_delete_lobby(self):
        tmp_user = AuthUserFactory()
        game = GameFactory()
        lobby = LobbyFactory(game=game, created_by=tmp_user)
        match = MatchFactory(game=game, lobby=lobby)
        lid, mid = lobby.id, match.id
        lobby.delete()
        self.assertFalse(Lobby.objects.filter(id=lid).exists())
        self.assertFalse(Match.objects.filter(id=mid).exists())

    # Cascade-delete behavior when Leaderboard is deleted
    def test_cascade_delete_leaderboard(self):
        lb = LeaderboardFactory(game=self.game)
        tmp_user = AuthUserFactory()
        prof = UserProfileFactory(user=tmp_user)
        entry = LeaderboardEntryFactory(leaderboard=lb, user=prof)
        eid = entry.id
        lb.delete()
        self.assertFalse(LeaderboardEntry.objects.filter(id=eid).exists())

    # Cascade-delete behavior when UserProfile is deleted
    def test_cascade_delete_user_profile_to_metric_scores(self):
        tmp_user = AuthUserFactory()
        prof = UserProfileFactory(user=tmp_user)
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

    # Cascade-delete behavior when AuthUser is deleted
    def test_cascade_delete_auth_user_to_user_profile(self):
        tmp_user = AuthUserFactory()
        prof = UserProfileFactory(user=tmp_user)
        pid = prof.id
        tmp_user.delete()
        self.assertFalse(UserProfile.objects.filter(id=pid).exists())

    # Verify related_name and reverse lookup relationships
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

    # Verify full field assignment at creation for UserProfile
    def test_user_profile_creation_all_fields(self):
        tmp_user = AuthUserFactory()
        prof = UserProfileFactory(user=tmp_user, bio="A test bio.")
        self.assertEqual(prof.user_id, tmp_user.id)
        self.assertEqual(prof.bio, "A test bio.")
        self.assertIsNotNone(prof.date_joined)

    # Verify full field assignment at creation for Game
    def test_game_creation_all_fields(self):
        g2 = GameFactory(name="FullGame", description="desc", min_players=2, max_players=4, complexity=3)
        self.assertEqual(g2.name, "FullGame")
        self.assertEqual(g2.description, "desc")
        self.assertEqual(g2.min_players, 2)
        self.assertEqual(g2.max_players, 4)
        self.assertEqual(g2.complexity, 3)

    # Verify full field assignment at creation for Lobby
    def test_lobby_creation_all_fields(self):
        tmp_user = AuthUserFactory()
        g3 = GameFactory()
        l3 = LobbyFactory(game=g3, created_by=tmp_user)
        self.assertEqual(l3.game, g3)
        self.assertEqual(l3.created_by, tmp_user)
        self.assertEqual(l3.min_players, g3.min_players)
        self.assertEqual(l3.max_players, g3.max_players)

    # Verify full field assignment at creation for Match
    def test_match_creation_all_fields(self):
        tmp_user = AuthUserFactory()
        g4 = GameFactory()
        l4 = LobbyFactory(game=g4, created_by=tmp_user)
        m4 = MatchFactory(game=g4, lobby=l4)
        self.assertEqual(m4.game, g4)
        self.assertEqual(m4.lobby, l4)
        self.assertTrue(timezone.now() - m4.date_played < datetime.timedelta(seconds=5))

    # Verify full field assignment at creation for MetricScore
    def test_metric_score_creation_all_fields(self):
        ms = MetricScore.objects.get(id=self.metric_score.id)
        self.assertEqual(ms.score, self.metric_score.score)
        self.assertEqual(ms.leaderboard_entry_id, self.entry.id)
        self.assertEqual(ms.user_id, self.user_profile.id)
        self.assertEqual(ms.metric_id, self.metric.id)
        self.assertEqual(ms.match_id, self.match.id)


# ========== TESTS FOR LEADERBOARD PRIVACY SETTING (LPS) ==========
# Hierarchy of privacy settings:
#   1. Specific leaderboard Setting (highest priority)
#   2. Game-level setting
#   3. Global setting (lowest priority)


@pytest.mark.django_db
def test_LPS_get_user_setting_specific_leaderboard():
    """
    Testing that the method get_user_setting returns the correct setting
    when a specific leaderboard is provided.
    If all game and leaderboard are provided, the specific leaderboard setting
    should be returned.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    specific_setting = LeaderboardSpecificPrivacySettingFactory(
        user=user, game=game, leaderboard=leaderboard, complete_opt_out=True, display_as_anonymous=False
    )
    GamePrivacySettingFactory(user=user, game=game, complete_opt_out=False, display_as_anonymous=False)
    GlobalPrivacySettingFactory(user=user, complete_opt_out=False, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == specific_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_game_level():
    """
    Testing that the method get_user_setting returns the correct setting
    when a game is provided.
    If only the game is provided, the setting for it should be returned.
    """
    user = UserProfileFactory()
    game = GameFactory()
    LeaderboardFactory(game=game)
    game_setting = GamePrivacySettingFactory(user=user, game=game, complete_opt_out=True, display_as_anonymous=False)
    GlobalPrivacySettingFactory(user=user, complete_opt_out=False, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game)

    assert test_setting == game_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_global():
    """
    Testing that the method get_user_setting returns the correct setting
    when neither a game nor a leaderboard are provided.
    It should return the global setting.
    """
    user = UserProfileFactory()
    game = GameFactory()
    LeaderboardFactory(game=game)
    global_setting = GlobalPrivacySettingFactory(user=user, complete_opt_out=True, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user)

    assert test_setting == global_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_fallback_to_game_leaderboard_missing():
    """
    Testing that even if a leaderboard is provided, but there is no specific
    setting for it, the method get_user_setting will fall back to the
    game-level setting.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    game_setting = GamePrivacySettingFactory(user=user, game=game, complete_opt_out=True, display_as_anonymous=False)
    GlobalPrivacySettingFactory(user=user, complete_opt_out=False, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == game_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_fallback_to_global_game_missing():
    """
    Testing that even if a leaderboard and game are provided, but there is no specific
    setting for it, the method get_user_setting will fall back to the
    global-level setting.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    global_setting = GlobalPrivacySettingFactory(user=user, complete_opt_out=True, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == global_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_none():
    """
    What happens when no settings are created for the user?
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    assert LeaderboardPrivacySetting.get_user_setting(user) is None
    assert LeaderboardPrivacySetting.get_user_setting(user, game) is None
    assert LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard) is None


# ===========================================================
