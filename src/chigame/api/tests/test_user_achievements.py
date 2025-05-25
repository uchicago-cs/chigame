from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chigame.achievements.models import UserAchievement
from chigame.api.tests.factories import AchievementFactory, GameFactory, UserAchievementFactory, UserFactory

# Local application/library specific imports


class UserAchievementTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.game = GameFactory()
        self.achievement = AchievementFactory(game=self.game)
        self.user_achievement = UserAchievementFactory()

    def test_create_user_achievement_success(self):
        data = {
            "user": self.user.id,
            "pinned": False,
            "progress": 0,
        }
        response = self.client.post(
            reverse("api-user-achievement-assignment", kwargs={"game_id": self.game.id, "pk": self.achievement.id}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Achievement created successfully!")
        self.assertEqual(response.data["data"]["user"], self.user.id)
        self.assertEqual(response.data["data"]["progress"], 0)

    def test_create_duplicate_user_achievement_fails(self):
        UserAchievementFactory(user=self.user, achievement=self.achievement)
        data = {"user": self.user.id}
        response = self.client.post(
            reverse("api-user-achievement-assignment", kwargs={"game_id": self.game.id, "pk": self.achievement.id}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("already exists", response.data["error"])

    def test_create_user_achievement_invalid_user(self):
        data = {"user": 9999}  # Nonexistent user ID
        response = self.client.post(
            reverse("api-user-achievement-assignment", kwargs={"game_id": self.game.id, "pk": self.achievement.id}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user_achievement_invalid_achievement(self):
        # Using an achievement ID that does not exist in the URL
        data = {"user": self.user.id}
        response = self.client.post(
            reverse("api-user-achievement-assignment", kwargs={"game_id": self.game.id, "pk": 9999}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_achievement(self):
        response = self.client.get(
            reverse(
                "api-user-achievements-edit",
                kwargs={"user_id": self.user_achievement.user.id, "pk": self.user_achievement.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user_achievement.id)

    def test_update_user_achievement(self):
        response = self.client.patch(
            reverse(
                "api-user-achievements-edit",
                kwargs={"user_id": self.user_achievement.user.id, "pk": self.user_achievement.id},
            ),
            {"pinned": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["pinned"])

    def test_delete_user_achievement(self):
        response = self.client.delete(
            reverse(
                "api-user-achievements-edit",
                kwargs={"user_id": self.user_achievement.user.id, "pk": self.user_achievement.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserAchievement.objects.filter(id=self.user_achievement.id).exists())

    def test_retrieve_nonexistent_user_achievement(self):
        response = self.client.get(
            reverse("api-user-achievements-edit", kwargs={"user_id": self.user_achievement.user.id, "pk": 9999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_achievements_success(self):
        achievements = AchievementFactory.create_batch(3, game=self.game)

        user_achievements = [UserAchievementFactory(user=self.user, achievement=a) for a in achievements]

        assert len(user_achievements) != 0
        response = self.client.get(reverse("api-user-achievements", kwargs={"pk": self.user.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for achievement in response.data:
            self.assertIn("id", achievement)
            self.assertIn("achievement", achievement)
            self.assertIn("game", achievement)
            self.assertIn("pinned", achievement)
            self.assertIn("date_earned", achievement)
            self.assertIn("last_updated", achievement)
            self.assertIn("progress", achievement)

    def test_get_user_achievements_invalid_user(self):
        invalid_url = reverse("api-user-achievements", kwargs={"pk": 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
