from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from chigame.games.models import Game, Lobby, Match, Tournament

User = get_user_model()


class MatchTimingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", email="user1@test.com", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", email="user2@test.com", password="testpass123")

        self.game = Game.objects.create(
            name="Test Game",
            description="Test Description",
            min_players=2,
            max_players=2,
            complexity=Decimal("2.50"),
            image="/static/images/no_picture_available.png",
        )

        self.lobby = Lobby.objects.create(
            name="Test Lobby",
            game=self.game,
            created_by=self.user1,
            min_players=2,
            max_players=2,
            match_status=Lobby.Lobbied,
        )
        self.lobby.members.add(self.user1, self.user2)

    def test_match_timing_on_status_change(self):
        """Test that match timing is updated when lobby status changes"""
        match = Match.objects.create(game=self.game, lobby=self.lobby, date_played=timezone.now())
        match.players.add(self.user1, self.user2)

        self.lobby.match_status = Lobby.Viewable
        self.lobby.save()

        match.refresh_from_db()
        self.assertIsNotNone(match.start_time)
        self.assertIsNone(match.end_time)
        self.assertIsNone(match.duration)

        self.lobby.match_status = Lobby.Finished
        self.lobby.save()

        match.refresh_from_db()
        self.assertIsNotNone(match.start_time)
        self.assertIsNotNone(match.end_time)
        self.assertIsNotNone(match.duration)
        self.assertGreater(match.duration.total_seconds(), 0)

    def test_match_timing_via_api(self):
        """Test match timing updates through the update_match_status view"""
        match = Match.objects.create(game=self.game, lobby=self.lobby, date_played=timezone.now())
        match.players.add(self.user1, self.user2)

        response = self.client.post(
            reverse("update_match_status", kwargs={"pk": self.lobby.pk}),
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 200)

        match.refresh_from_db()
        self.assertIsNotNone(match.start_time)
        self.assertIsNone(match.end_time)

        self.lobby.members.remove(self.user2)
        response = self.client.post(
            reverse("update_match_status", kwargs={"pk": self.lobby.pk}),
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 200)

        match.refresh_from_db()
        self.assertIsNotNone(match.start_time)
        self.assertIsNotNone(match.end_time)
        self.assertIsNotNone(match.duration)
        self.assertGreater(match.duration.total_seconds(), 0)

    def test_match_timing_in_game_flow(self):
        """Test match timing in the context of a game being played"""
        match = Match.objects.create(game=self.game, lobby=self.lobby, date_played=timezone.now())
        match.players.add(self.user1, self.user2)

        self.lobby.match_status = Lobby.Viewable
        self.lobby.save()

        self.client.login(username="user1", password="testpass123")
        response = self.client.post(reverse("flip-result", kwargs={"pk": self.lobby.pk}), {"user_guess": "heads"})
        self.assertEqual(response.status_code, 302)

        match.refresh_from_db()
        self.assertIsNotNone(match.start_time)
        self.assertIsNone(match.end_time)

        self.client.login(username="user2", password="testpass123")
        response = self.client.post(reverse("flip-result", kwargs={"pk": self.lobby.pk}), {"user_guess": "tails"})
        self.assertEqual(response.status_code, 302)

        self.lobby.match_status = Lobby.Finished
        self.lobby.save()

        match.refresh_from_db()
        self.assertIsNotNone(match.start_time)
        self.assertIsNotNone(match.end_time)
        self.assertIsNotNone(match.duration)
        self.assertGreater(match.duration.total_seconds(), 0)

    def test_fastest_match(self):
        """Test getting the fastest completed match"""
        match1 = Match.objects.create(
            game=self.game,
            lobby=self.lobby,
            date_played=timezone.now(),
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(minutes=5),
            duration=timedelta(minutes=5),
        )
        match1.players.add(self.user1, self.user2)

        lobby2 = Lobby.objects.create(
            name="Test Lobby 2",
            game=self.game,
            created_by=self.user1,
            min_players=2,
            max_players=2,
            match_status=Lobby.Finished,
        )
        lobby2.members.add(self.user1, self.user2)

        match2 = Match.objects.create(
            game=self.game,
            lobby=lobby2,
            date_played=timezone.now(),
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(minutes=10),
            duration=timedelta(minutes=10),
        )
        match2.players.add(self.user1, self.user2)

        fastest_match = Match.get_fastest_match()
        self.assertEqual(fastest_match, match1)
        self.assertEqual(fastest_match.duration, timedelta(minutes=5))

    def test_slowest_match(self):
        """Test getting the slowest completed match"""
        match1 = Match.objects.create(
            game=self.game,
            lobby=self.lobby,
            date_played=timezone.now(),
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(minutes=5),
            duration=timedelta(minutes=5),
        )
        match1.players.add(self.user1, self.user2)

        lobby2 = Lobby.objects.create(
            name="Test Lobby 2",
            game=self.game,
            created_by=self.user1,
            min_players=2,
            max_players=2,
            match_status=Lobby.Finished,
        )
        lobby2.members.add(self.user1, self.user2)

        match2 = Match.objects.create(
            game=self.game,
            lobby=lobby2,
            date_played=timezone.now(),
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(minutes=10),
            duration=timedelta(minutes=10),
        )
        match2.players.add(self.user1, self.user2)

        slowest_match = Match.get_slowest_match()
        self.assertEqual(slowest_match, match2)
        self.assertEqual(slowest_match.duration, timedelta(minutes=10))


class MatchStatsViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", email="user1@test.com", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", email="user2@test.com", password="testpass123")

        self.game = Game.objects.create(
            name="Test Game", description="Test Description", min_players=2, max_players=2, complexity=Decimal("2.50")
        )

        now = timezone.now()
        self.tournament = Tournament.objects.create(
            name="Test Tournament",
            game=self.game,
            registration_start_date=now - timedelta(days=2),
            registration_end_date=now - timedelta(days=1),
            tournament_start_date=now - timedelta(days=1),
            tournament_end_date=now,  # Ended now
            max_players=2,
        )
        self.tournament.players.add(self.user1, self.user2)

        self.lobby1 = Lobby.objects.create(
            name="Test Lobby 1",
            game=self.game,
            created_by=self.user1,
            min_players=2,
            max_players=2,
            match_status=Lobby.Finished,
        )
        self.lobby1.members.add(self.user1, self.user2)

        self.lobby2 = Lobby.objects.create(
            name="Test Lobby 2",
            game=self.game,
            created_by=self.user1,
            min_players=2,
            max_players=2,
            match_status=Lobby.Finished,
        )
        self.lobby2.members.add(self.user1, self.user2)

        self.match1 = Match.objects.create(
            game=self.game,
            lobby=self.lobby1,
            date_played=now - timedelta(minutes=30),
            start_time=now - timedelta(minutes=30),
            end_time=now - timedelta(minutes=25),
            duration=timedelta(minutes=5),
        )
        self.match1.players.add(self.user1, self.user2)
        self.tournament.matches.add(self.match1)

        self.match2 = Match.objects.create(
            game=self.game,
            lobby=self.lobby2,
            date_played=now - timedelta(minutes=20),
            start_time=now - timedelta(minutes=20),
            end_time=now - timedelta(minutes=5),  # 15 minutes duration
            duration=timedelta(minutes=15),
        )
        self.match2.players.add(self.user1, self.user2)
        self.tournament.matches.add(self.match2)

        self.client = Client()

    def test_fastest_match(self):
        """Test that the fastest match is correctly identified"""
        now = timezone.now()
        lobby3 = Lobby.objects.create(
            name="Test Lobby 3",
            game=self.game,
            created_by=self.user1,
            min_players=2,
            max_players=2,
            match_status=Lobby.Finished,
        )
        lobby3.members.add(self.user1, self.user2)

        fastest_match = Match.objects.create(
            game=self.game,
            lobby=lobby3,
            date_played=now - timedelta(minutes=10),
            start_time=now - timedelta(minutes=10),
            end_time=now - timedelta(minutes=8),  # 2 minutes duration
            duration=timedelta(minutes=2),
        )
        fastest_match.players.add(self.user1, self.user2)
        self.tournament.matches.add(fastest_match)

        response = self.client.get(reverse("tournament-match-stats", kwargs={"pk": self.tournament.pk}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["fastest_match"], fastest_match)
        self.assertEqual(response.context["fastest_match"].duration.total_seconds() / 60, 2)

    def test_slowest_match(self):
        """Test that the slowest match is correctly identified"""
        now = timezone.now()
        lobby3 = Lobby.objects.create(
            name="Test Lobby 3",
            game=self.game,
            created_by=self.user1,
            min_players=2,
            max_players=2,
            match_status=Lobby.Finished,
        )
        lobby3.members.add(self.user1, self.user2)

        slowest_match = Match.objects.create(
            game=self.game,
            lobby=lobby3,
            date_played=now - timedelta(minutes=25),
            start_time=now - timedelta(minutes=25),
            end_time=now - timedelta(minutes=5),  # 20 minutes duration
            duration=timedelta(minutes=20),
        )
        slowest_match.players.add(self.user1, self.user2)
        self.tournament.matches.add(slowest_match)

        response = self.client.get(reverse("tournament-match-stats", kwargs={"pk": self.tournament.pk}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["slowest_match"], slowest_match)
        self.assertEqual(response.context["slowest_match"].duration.total_seconds() / 60, 20)

    def test_match_stats_view(self):
        response = self.client.get(reverse("tournament-match-stats", kwargs={"pk": self.tournament.pk}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["tournament"], self.tournament)
        self.assertEqual(response.context["fastest_match"], self.match1)  # 5 minutes
        self.assertEqual(response.context["slowest_match"], self.match2)  # 15 minutes
        self.assertEqual(len(response.context["all_matches"]), 2)

    def test_match_stats_view_ongoing_tournament(self):
        now = timezone.now()
        ongoing_tournament = Tournament.objects.create(
            name="Ongoing Tournament",
            game=self.game,
            registration_start_date=now - timedelta(days=2),
            registration_end_date=now - timedelta(days=1),
            tournament_start_date=now - timedelta(days=1),
            tournament_end_date=now + timedelta(days=1),  # Ends in the future
            max_players=2,
        )

        response = self.client.get(reverse("tournament-match-stats", kwargs={"pk": ongoing_tournament.pk}))
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_match_stats_view_no_matches(self):
        now = timezone.now()
        empty_tournament = Tournament.objects.create(
            name="Empty Tournament",
            game=self.game,
            registration_start_date=now - timedelta(days=2),
            registration_end_date=now - timedelta(days=1),
            tournament_start_date=now - timedelta(days=1),
            tournament_end_date=now,  # Ended now
            max_players=2,
        )

        response = self.client.get(reverse("tournament-match-stats", kwargs={"pk": empty_tournament.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["fastest_match"])
        self.assertIsNone(response.context["slowest_match"])
        self.assertEqual(len(response.context["all_matches"]), 0)
