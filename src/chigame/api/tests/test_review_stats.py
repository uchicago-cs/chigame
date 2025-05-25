from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chigame.api.tests.factories import GameFactory, ReviewFactory, UserFactory


class GameReviewStatsTests(APITestCase):
    def test_review_stats_returns_correct_data(self):
        game = GameFactory()
        user = UserFactory()
        self.client.force_authenticate(user=user)

        # Create public reviews with ratings
        ReviewFactory.create_batch(3, game=game, user=user, rating=4, is_public=True)
        ReviewFactory(game=game, user=user, rating=2.5, is_public=True)

        # Create a review without a rating (should be ignored in average)
        ReviewFactory(game=game, user=user, rating=None, is_public=True)

        # Create a private review (should be ignored completely)
        ReviewFactory(game=game, user=user, rating=5, is_public=False)

        url = reverse("api-game-review-stats", args=[game.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["popularity"], 5)  # all public reviews
        self.assertEqual(float(response.data["average_rating"]), 3.62)  # (4+4+4+2.5)/4 truncated to 2 decimal places

    def test_review_stats_no_reviews(self):
        game = GameFactory()
        url = reverse("api-game-review-stats", args=[game.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["popularity"], 0)
        self.assertIsNone(response.data["average_rating"])

    def test_review_stats_unauthenticated_access(self):
        game = GameFactory()
        url = reverse("api-game-review-stats", args=[game.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_stats_404_for_nonexistent_game(self):
        url = reverse("api-game-review-stats", args=[99999])  # assuming this ID doesn't exist
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_stats_405_post_not_allowed(self):
        game = GameFactory()
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("api-game-review-stats", args=[game.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
