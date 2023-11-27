# from django.test import TestCase

# Create your tests here.

# Compare this snippet from src/chigame/api/tests.py:
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chigame.api.tests.factories import GameFactory
from chigame.games.models import Game


class GameTests(APITestCase):
    def check_equal(self, obj, expected: dict):
        """
        Helper function to check that the object data matches the expected data.
        """
        for key in expected:
            self.assertEqual(getattr(obj, key), expected[key])

    # def test_get_game(self):
    #     """
    #     Ensure we can get a game object.
    #     """

    #     # Create a game object
    #     game = GameFactory()

    #     # Get the game object
    #     url = reverse("api-game-detail", args=[game.id])
    #     response = self.client.get(url, format="json")

    #     # Check that the game object was retrieved correctly
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(Game.objects.count(), 1)
    #     self.check_equal(Game.objects.get(), response.data)

    def test_update_game(self):
        """
        Ensure we can update a game object.
        """

        # Create a game object
        game = GameFactory()

        # Update the game object
        url = reverse("api-game-detail", args=[game.id])
        updated_data = {"name": "The Witcher 3: Wild Hunt", "max_players": 10}
        response = self.client.patch(url, updated_data, format="json")

        # Check that the game object was updated correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_game = Game.objects.get(id=game.id)

        self.assertIsNotNone(updated_game)
        self.check_equal(updated_game, updated_data)

    def test_delete_game(self):
        """
        Ensure we can delete a game object.
        """

        # Create a game object
        game = GameFactory()

        # Delete the game object
        url = reverse("api-game-detail", args=[game.id])
        response = self.client.delete(url, format="json")

        # Check that the game object was deleted correctly
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Game.objects.count(), 0)

    # def test_get_game_list(self):
    #     """
    #     Ensure we can get a list of game objects.
    #     """
    #     url = reverse("api-game-list")

    #     # create three game objects
    #     game1 = GameFactory()
    #     game2 = GameFactory()
    #     game3 = GameFactory()

    #     # Get the game object list
    #     url = reverse("api-game-list")
    #     response = self.client.get(url, format="json")

    #     # Check that the game object list was retrieved correctly
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # test that the game object list contains the two game objects we created
    #     self.check_equal(game1, response.data[0])
    #     self.check_equal(game2, response.data[1])
    #     self.check_equal(game3, response.data[2])
