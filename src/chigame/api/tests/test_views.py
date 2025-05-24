from django.test import TestCase, Client
from django.urls import reverse
from chigame.users.models import User
from .factories import *
import pytest

class UserViewTests(APITestCase):
    def test_user_list_view(self):
        UserFactory()
        url = reverse("api-user-list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_user_create_view(self):
        url = reverse("api-user-list")
        data = {"email": "new@b.com", "password": "testpass123"}
        response = self.client.post(url, data)
        assert response.ok


class GameViewTests(APITestCase):
    def test_game_list_view(self):
        GameFactory()
        url = reverse("api-game-list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_game_create_view(self):
        url = reverse("api-game-list")
        data = {"name": "New Game", "description": "desc", "min_players": 1, "max_players": 2}
        response = self.client.post(url, data)
        assert response.ok


class ReviewViewTests(APITestCase):
    def test_review_list_view(self):
        ReviewFactory()
        url = reverse("api-review-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_review_create_view(self):
        game = GameFactory()
        user = UserFactory()
        url = reverse("api-review-list")
        data = {"game": game.id, "user": user.id, "rating": 5, "review": "Great!"}
        response = self.client.post(url, data)
        assert response.ok


class AchievementViewTests(APITestCase):
    def test_achievement_list_view(self):
        AchievementFactory()
        url = reverse("api-achievement-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_achievement_create_view(self):
        url = reverse("api-achievement-list")
        data = {"name": "First Win", "description": "Win a game", "rarity": 1, "threshold": 1}
        response = self.client.post(url, data)
        assert response.ok


class UserAchievementViewTests(APITestCase):
    def test_user_achievement_list_view(self):
        UserAchievementFactory()
        url = reverse("api-userachievement-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_user_achievement_create_view(self):
        user = UserFactory()
        achievement = AchievementFactory()
        url = reverse("api-userachievement-list")
        data = {"user": user.id, "achievement": achievement.id}
        response = self.client.post(url, data)
        assert response.ok


class FeedbackViewTests(APITestCase):
    def test_feedback_list_view(self):
        FeedbackFactory()
        url = reverse("api-feedback-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_feedback_create_view(self):
        tournament = TournamentFactory()
        user = UserFactory()
        url = reverse("api-feedback-list")
        data = {"tournament": tournament.id, "user": user.id, "rating": 5}
        response = self.client.post(url, data)
        assert response.ok


class TournamentViewTests(APITestCase):
    def test_tournament_list_view(self):
        TournamentFactory()
        url = reverse("api-tournament-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_tournament_create_view(self):
        game = GameFactory()
        url = reverse("api-tournament-list")
        data = {
            "name": "T1", "game": game.id,
            "registration_start_date": "2024-01-01T00:00:00Z",
            "registration_end_date": "2024-01-02T00:00:00Z",
            "tournament_start_date": "2024-01-03T00:00:00Z",
            "tournament_end_date": "2024-01-04T00:00:00Z",
            "max_players": 4, "description": "desc", "rules": "rules", "draw_rules": "draw", "num_winner": 1
        }
        response = self.client.post(url, data)
        assert response.ok


class LiveChatViewTests(APITestCase):
    def test_livechat_list_view(self):
        LiveChatFactory()
        url = reverse("api-livechat-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_livechat_create_view(self):
        url = reverse("api-livechat-list")
        data = {"name": "Test Chat"}
        response = self.client.post(url, data)
        assert response.ok

  
