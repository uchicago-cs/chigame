from django.urls import reverse

# Related third party imports
from rest_framework import status
from rest_framework.test import APITestCase

from chigame.achievements.models import Achievement

# Local application/library specific imports
from chigame.api.tests.factories import AchievementFactory, GameFactory


class AchievementTests(APITestCase):
    def setUp(self):
        self.game = GameFactory()
        self.other_game = GameFactory()
        self.achievements = AchievementFactory.create_batch(3, game=self.game)
        AchievementFactory.create_batch(2, game=self.other_game)

    def test_list_achievements_for_valid_game(self):
        url = reverse("api-game-achievements", kwargs={"pk": self.game.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        returned_names = {a["name"] for a in response.data["results"]}
        expected_names = {a.name for a in self.achievements}
        self.assertSetEqual(returned_names, expected_names)

    def test_list_achievements_for_game_with_none(self):
        new_game = GameFactory()
        url = reverse("api-game-achievements", kwargs={"pk": new_game.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_achievements_invalid_game_id(self):
        invalid_id = 99999
        url = reverse("api-game-achievements", kwargs={"pk": invalid_id})
        response = self.client.get(url)

        # Still returns 200 with empty list since queryset is filtered, not looked up
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create_achievement_success(self):
        data = {"name": "New Achievement", "description": "A cool achievement", "rarity": 3, "threshold": 10.0}
        response = self.client.post(
            reverse("api-game-achievement-create", kwargs={"pk": self.game.id}), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["name"], data["name"])
        self.assertEqual(response.data["data"]["description"], data["description"])
        self.assertEqual(response.data["data"]["rarity"], data["rarity"])
        self.assertEqual(float(response.data["data"]["threshold"]), data["threshold"])

    def test_create_duplicate_achievement(self):
        Achievement.objects.create(
            name="Duplicate Achievement", description="Already exists", rarity=2, threshold=5, game=self.game
        )
        data = {"name": "Duplicate Achievement", "description": "Try to create duplicate", "rarity": 2, "threshold": 5}
        response = self.client.post(
            reverse("api-game-achievement-create", kwargs={"pk": self.game.id}), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("already exists", response.data["error"])

    def test_create_missing_name_field(self):
        data = {"description": "No name provided", "rarity": 1, "threshold": 1.0}
        response = self.client.post(
            reverse("api-game-achievement-create", kwargs={"pk": self.game.id}), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
