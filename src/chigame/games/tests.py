from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from chigame.games.models import Game, Lobby, Match, Tournament

from .models import Category, Feedback, Mechanic, Person, Player
from .views import get_recommended_games

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


class FeedbackTests(TestCase):
    def setUp(self):
        # Create users
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="pass")
        self.user = User.objects.create_user(username="user", email="user@example.com", password="pass")
        self.other = User.objects.create_user(username="other", email="other@example.com", password="pass")
        self.admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass")

        assert self.client.login(email="user@example.com", password="pass"), "Login failed for user"
        self.client.logout()
        assert self.client.login(email="admin@example.com", password="pass"), "Login failed for admin"
        self.client.logout()

        # Create a game
        self.game = Game.objects.create(
            name="Test Game",
            description="desc",
            min_players=2,
            max_players=4,
            complexity=2.5,
        )

        now = timezone.now()
        # Create tournament
        self.tournament = Tournament.objects.create(
            name="Test Tournament",
            game=self.game,
            registration_start_date=now + timedelta(days=1),
            registration_end_date=now + timedelta(days=2),
            tournament_start_date=now + timedelta(days=3),
            tournament_end_date=now + timedelta(days=4),
            max_players=16,
            description="desc",
            rules="rules",
            draw_rules="draw",
            num_winner=1,
            archived=False,
            created_by=self.owner,
        )

        # URLs
        self.submit_url = reverse("submit-feedback", args=[self.tournament.id])
        self.feedback_list_url = reverse("tournament-feedback-list", args=[self.tournament.id])
        self.user_feedback_url = reverse("user-feedback-list")

    def test_feedback_form_validation(self):
        self.client.login(email="user@example.com", password="pass")
        # Empty comment
        response = self.client.post(self.submit_url, {"content": "", "rating": 3})
        self.assertEqual(response.status_code, 302)  # Redirects with error message

        # Rating out of range
        response = self.client.post(self.submit_url, {"content": "Nice!", "rating": 6})
        self.assertEqual(response.status_code, 302)  # Redirects with error message

    def test_feedback_submission_and_appearance(self):
        logged_in = self.client.login(email="user@example.com", password="pass")
        self.assertTrue(logged_in)

        # Match this key to your view's form processing
        self.client.post(self.submit_url, {"content": "Great!", "rating": 5})

        feedback = Feedback.objects.filter(user=self.user, tournament=self.tournament).first()
        self.assertIsNotNone(feedback)

        self.client.logout()
        self.client.login(email="owner@example.com", password="pass")
        response = self.client.get(self.feedback_list_url)
        self.assertContains(response, "Great!")

    def test_unauthorized_edit_delete(self):
        self.client.login(email="user@example.com", password="pass")
        feedback = Feedback.objects.create(user=self.user, tournament=self.tournament, comment="Test", rating=4)
        self.client.logout()

        self.client.login(email="other@example.com", password="pass")
        update_url = reverse("update-feedback", args=[feedback.id])
        delete_url = reverse("delete-feedback", args=[feedback.id])

        response = self.client.post(update_url, {"content": "Hack", "rating": 3})
        self.assertEqual(response.status_code, 403)

        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_feedback(self):
        feedback = Feedback.objects.create(user=self.user, tournament=self.tournament, comment="To delete", rating=3)
        self.client.login(email="admin@example.com", password="pass")
        delete_url = reverse("delete-feedback", args=[feedback.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, self.user_feedback_url)
        self.assertFalse(Feedback.objects.filter(id=feedback.id).exists())

    def test_only_owner_can_see_all_feedback(self):
        Feedback.objects.create(user=self.user, tournament=self.tournament, comment="User feedback", rating=4)

        self.client.login(email="owner@example.com", password="pass")
        response = self.client.get(self.feedback_list_url)
        self.assertContains(response, "User feedback")

        self.client.logout()
        self.client.login(email="user@example.com", password="pass")
        response = self.client.get(self.feedback_list_url)
        self.assertEqual(response.status_code, 302)  # Redirects because user isn't the owner

    def test_user_can_only_see_and_edit_own_feedback(self):
        fb1 = Feedback.objects.create(user=self.user, tournament=self.tournament, comment="Mine", rating=5)
        fb2 = Feedback.objects.create(user=self.other, tournament=self.tournament, comment="Not mine", rating=3)

        self.client.login(email="user@example.com", password="pass")

        response = self.client.get(self.user_feedback_url)
        self.assertContains(response, "Mine")
        self.assertNotContains(response, "Not mine")

        update_url = reverse("update-feedback", args=[fb1.id])
        response = self.client.post(update_url, {"content": "Updated", "rating": 4})
        self.assertRedirects(response, self.user_feedback_url)
        fb1.refresh_from_db()
        self.assertEqual(fb1.comment, "Updated")

        update_url_other = reverse("update-feedback", args=[fb2.id])
        response = self.client.post(update_url_other, {"content": "Hack", "rating": 2})
        self.assertEqual(response.status_code, 403)


User = get_user_model()


class RecommendationSystemTest(TestCase):
    def setUp(self):
        # Create test categories
        self.category1 = Category.objects.create(name="Strategy")
        self.category2 = Category.objects.create(name="Card Game")
        self.category3 = Category.objects.create(name="Fantasy")

        # Create test mechanics
        self.mechanic1 = Mechanic.objects.create(name="Deck Building")
        self.mechanic2 = Mechanic.objects.create(name="Worker Placement")

        # Create test people
        self.person1 = Person.objects.create(name="Game Designer 1", person_role=1)

        # Create test games with various attributes - now with descriptions
        self.game1 = Game.objects.create(
            name="Base Game",
            description="This is the base game for testing",
            min_players=2,
            max_players=4,
            complexity=3.5,
            expected_playtime=60,
        )
        self.game1.categories.add(self.category1, self.category2)
        self.game1.mechanics.add(self.mechanic1)
        self.game1.people.add(self.person1)

        self.game2 = Game.objects.create(
            name="Similar Game",
            description="This game is very similar to the base game",
            min_players=2,
            max_players=4,
            complexity=3.2,
            expected_playtime=70,
        )
        self.game2.categories.add(self.category1, self.category2)
        self.game2.mechanics.add(self.mechanic1)
        self.game2.people.add(self.person1)

        self.game3 = Game.objects.create(
            name="Somewhat Similar",
            description="This game is somewhat similar to the base game",
            min_players=3,
            max_players=6,
            complexity=4.0,
            expected_playtime=90,
        )
        self.game3.categories.add(self.category1)
        self.game3.mechanics.add(self.mechanic2)

        self.game4 = Game.objects.create(
            name="Less Similar",
            description="This game is less similar to the base game",
            min_players=1,
            max_players=2,
            complexity=2.0,
            expected_playtime=30,
        )
        self.game4.categories.add(self.category3)

        # atest user
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpass")

    def test_recommendation_order(self):
        """Test that games are recommended in correct order based on similarity"""
        recommendations = get_recommended_games(self.game1)
        self.assertEqual(list(recommendations), [self.game2, self.game3, self.game4])

    def test_played_games_penalty(self):
        """Test that played games are deprioritized but not excluded"""
        # Create a lobby first (required for match)
        lobby = Lobby.objects.create(
            name="Test Lobby",
            game=self.game2,
            created_by=self.user,
            min_players=1,
            max_players=4,
            match_status=1,  # Assuming 1 is 'Lobbied' status
        )

        # Now create the match with this lobby
        match = Match.objects.create(
            game=self.game2, lobby=lobby, date_played="2023-01-01T12:00:00Z"  # Use the lobby we created
        )
        match.players.add(self.user)

        # Create player for this match
        Player.objects.create(user=self.user, match=match, outcome=Player.WIN)

        # Game2 should still be recommended but at a lower position
        recommendations = get_recommended_games(self.game1, user=self.user)
        self.assertIn(self.game2, recommendations)
        self.assertEqual(list(recommendations)[0], self.game3)  # game3 should now be first
