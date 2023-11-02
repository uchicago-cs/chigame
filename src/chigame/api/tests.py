# from django.test import TestCase

# Create your tests here.

# Compare this snippet from src/chigame/api/tests.py:
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chigame.games.models import Game


class GameTests(APITestCase):
    def test_create_game(self):
        """
        Ensure we can create a new game object.
        """

        # Create a game object
        url = reverse("game-list")
        data = {"name": "The Witcher 3", "description": "Geralt of Rivia", "min_players": 1, "max_players": 4}
        response = self.client.post(url, data, format="json")
        # Check that the game object was created correctly
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Game.objects.get().name, "The Witcher 3")
        self.assertEqual(Game.objects.get().description, "Geralt of Rivia")
        self.assertEqual(Game.objects.get().min_players, 1)
        self.assertEqual(Game.objects.get().max_players, 4)

    def test_get_game(self):
        """
        Ensure we can get a game object.
        """

        # Create a game object
        url = reverse("game-list")
        data = {"name": "The Witcher 3", "description": "Geralt of Rivia", "min_players": 1, "max_players": 4}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the game object
        url = reverse("game-detail", kwargs={"pk": 1})
        response = self.client.get(url, format="json")

        # Check that the game object was retrieved correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Game.objects.get().name, "The Witcher 3")
        self.assertEqual(Game.objects.get().description, "Geralt of Rivia")
        self.assertEqual(Game.objects.get().min_players, 1)
        self.assertEqual(Game.objects.get().max_players, 4)

    def test_update_game(self):
        """
        Ensure we can update a game object.
        """

        # Create a game object
        url = reverse("game-list")
        data = {"name": "The Witcher 3", "description": "Geralt of Rivia", "min_players": 1, "max_players": 4}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update the game object
        url = reverse("game-detail", kwargs={"pk": 1})
        data = {"name": "The Witcher 3: Wild Hunt", "max_players": 5}
        response = self.client.patch(url, data, format="json")

        # Check that the game object was updated correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Game.objects.get().name, "The Witcher 3: Wild Hunt")
        self.assertEqual(Game.objects.get().description, "Geralt of Rivia")
        self.assertEqual(Game.objects.get().min_players, 1)
        self.assertEqual(Game.objects.get().max_players, 5)

    def test_delete_game(self):
        """
        Ensure we can delete a game object.
        """

        # Create a game object
        url = reverse("game-list")
        data = {"name": "The Witcher 3", "description": "Geralt of Rivia", "min_players": 1, "max_players": 4}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Delete the game object
        url = reverse("game-detail", kwargs={"pk": 1})
        response = self.client.delete(url, format="json")

        # Check that the game object was deleted correctly
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Game.objects.count(), 0)

    def test_get_game_list(self):
        """
        Ensure we can get a list of game objects.
        """

        # Create a game object
        url = reverse("game-list")
        data = {"name": "The Witcher 3", "description": "Geralt of Rivia", "min_players": 1, "max_players": 4}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the game object list
        url = reverse("game-list")
        response = self.client.get(url, format="json")

        # Check that the game object list was retrieved correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [{"name": "The Witcher 3", "description": "Geralt of Rivia", "min_players": 1, "max_players": 4}],
        )
