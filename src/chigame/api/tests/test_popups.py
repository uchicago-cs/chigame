from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chigame.api.serializers import PopUpInfoSerializer
from chigame.api.tests.factories import GameFactory, UserFactory


class PopupsTests(APITestCase):
    def test_get_popups_200(self):
        game = GameFactory(
            min_players=2,
            max_players=5,
            complexity=3.2,
            min_playtime=15,
            max_playtime=30,
            description="This is a test game",
        )
        url = reverse("api-game-popups", args=[game.id])
        response = self.client.get(url)
        expected = PopUpInfoSerializer(
            {
                "min_players": 2,
                "max_players": 5,
                "complexity": 3.2,
                "min_playtime": 15,
                "max_playtime": 30,
                "description": "This is a test game",
            }
        ).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def test_get_popups_404(self):
        url = reverse("api-game-popups", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_popups_405(self):
        game = GameFactory()
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("api-game-popups", args=[game.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
