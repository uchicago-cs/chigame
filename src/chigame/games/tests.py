from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Feedback, Game, Lobby, Match, Mechanic, Person, Player, Tournament
from .views import get_recommended_games


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
        super().setUp()

        # clear any leftover Twine game that may have been inserted by migrations
        Game.objects.filter(name="Twine Test Game").delete()

        # clear any pre-existing test/migrated games
        Game.objects.all().delete()

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
        recommendations = [
            game for game in get_recommended_games(self.game1, user=self.user) if game.name != "Twine Test Game"
        ]
        self.assertIn(self.game2, recommendations)
        self.assertEqual(list(recommendations)[0], self.game3)  # game3 should now be first
