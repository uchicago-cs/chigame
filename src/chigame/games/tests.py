from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Feedback, Game, Tournament, User


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
