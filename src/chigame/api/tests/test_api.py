# from django.test import TestCase

# Create your tests here.

# Compare this snippet from src/chigame/api/tests.py:
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chigame.api.tests.factories import ChatFactory, GameFactory, TournamentFactory, UserFactory
from chigame.games.models import Game, Message, User


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


class ChatTests(APITestCase):
    def test_create_message(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.game = GameFactory()
        self.tournament = TournamentFactory(game=self.game)
        self.chat = ChatFactory(tournament=self.tournament)
        self.endpoint = reverse("api-chat-list")

        data1 = {
            "sender": self.user1.email,
            "tournament": self.tournament.id,
            "content": "test script 1!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data1, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data1["content"])
        self.assertEqual(data1["sender"], Message.objects.get(id=1).sender.email)
        self.assertEqual(data1["tournament"], Message.objects.get(id=1).chat.tournament.id)
        self.assertEqual(data1["update_on"], Message.objects.get(id=1).update_on)
        self.assertEqual(data1["content"], Message.objects.get(id=1).content)
        self.assertEqual(1, Message.objects.get(id=1).token_id)

        data2 = {
            "sender": self.user2.email,
            "tournament": self.tournament.id,
            "content": "test script 2!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data2, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data2["content"])
        self.assertEqual(data2["sender"], Message.objects.get(id=2).sender.email)
        self.assertEqual(data2["tournament"], Message.objects.get(id=2).chat.tournament.id)
        self.assertEqual(data2["update_on"], Message.objects.get(id=2).update_on)
        self.assertEqual(data2["content"], Message.objects.get(id=2).content)
        self.assertEqual(2, Message.objects.get(id=2).token_id)

        data3 = {
            "sender": self.user1.email,
            "tournament": self.tournament.id,
            "content": "test script 3!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data3, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data3["content"])
        self.assertEqual(data3["sender"], Message.objects.get(id=3).sender.email)
        self.assertEqual(data3["tournament"], Message.objects.get(id=3).chat.tournament.id)
        self.assertEqual(data3["update_on"], Message.objects.get(id=3).update_on)
        self.assertEqual(data3["content"], Message.objects.get(id=3).content)
        self.assertEqual(3, Message.objects.get(id=3).token_id)

        data4 = {
            "sender": self.user2.email,
            "tournament": self.tournament.id,
            "content": "test script 4!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data4, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data4["content"])
        self.assertEqual(data4["sender"], Message.objects.get(id=4).sender.email)
        self.assertEqual(data4["tournament"], Message.objects.get(id=4).chat.tournament.id)
        self.assertEqual(data4["update_on"], Message.objects.get(id=4).update_on)
        self.assertEqual(data4["content"], Message.objects.get(id=4).content)
        self.assertEqual(4, Message.objects.get(id=4).token_id)

    def test_delete_message(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.game = GameFactory()
        self.tournament = TournamentFactory(game=self.game)
        self.chat = ChatFactory(tournament=self.tournament)
        self.endpoint = reverse("api-chat-list")
        data1 = {
            "sender": self.user1.email,
            "tournament": self.tournament.id,
            "content": "test script 1!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data1, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data1["content"])
        self.assertEqual(data1["sender"], Message.objects.get(id=1).sender.email)
        self.assertEqual(data1["tournament"], Message.objects.get(id=1).chat.tournament.id)
        self.assertEqual(data1["update_on"], Message.objects.get(id=1).update_on)
        self.assertEqual(data1["content"], Message.objects.get(id=1).content)
        self.assertEqual(1, Message.objects.get(id=1).token_id)

        data2 = {
            "sender": self.user2.email,
            "tournament": self.tournament.id,
            "content": "test script 2!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data2, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data2["content"])
        self.assertEqual(data2["sender"], Message.objects.get(id=2).sender.email)
        self.assertEqual(data2["tournament"], Message.objects.get(id=2).chat.tournament.id)
        self.assertEqual(data2["update_on"], Message.objects.get(id=2).update_on)
        self.assertEqual(data2["content"], Message.objects.get(id=2).content)
        self.assertEqual(2, Message.objects.get(id=2).token_id)

        data3 = {
            "sender": self.user1.email,
            "tournament": self.tournament.id,
            "content": "test script 3!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data3, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data3["content"])
        self.assertEqual(data3["sender"], Message.objects.get(id=3).sender.email)
        self.assertEqual(data3["tournament"], Message.objects.get(id=3).chat.tournament.id)
        self.assertEqual(data3["update_on"], Message.objects.get(id=3).update_on)
        self.assertEqual(data3["content"], Message.objects.get(id=3).content)
        self.assertEqual(3, Message.objects.get(id=3).token_id)

        data4 = {
            "sender": self.user2.email,
            "tournament": self.tournament.id,
            "content": "test script 4!",
            "update_on": None,
        }

        response = self.client.post(self.endpoint, data4, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data4["content"])
        self.assertEqual(data4["sender"], Message.objects.get(id=4).sender.email)
        self.assertEqual(data4["tournament"], Message.objects.get(id=4).chat.tournament.id)
        self.assertEqual(data4["update_on"], Message.objects.get(id=4).update_on)
        self.assertEqual(data4["content"], Message.objects.get(id=4).content)
        self.assertEqual(4, Message.objects.get(id=4).token_id)

        delete1 = {"sender": self.user1.email, "tournament": self.tournament.id, "content": None, "update_on": 1}

        response = self.client.post(self.endpoint, delete1, format="json")

        self.assertEqual(5, Message.objects.count())
        self.assertEqual(delete1["sender"], Message.objects.get(id=5).sender.email)
        self.assertEqual(delete1["tournament"], Message.objects.get(id=5).chat.tournament.id)
        self.assertEqual(delete1["update_on"], Message.objects.get(id=5).update_on)
        self.assertEqual(delete1["content"], Message.objects.get(id=5).content)
        self.assertEqual(5, Message.objects.get(id=5).token_id)

        self.assertEqual(data1["sender"], Message.objects.get(id=1).sender.email)
        self.assertEqual(data1["tournament"], Message.objects.get(id=1).chat.tournament.id)
        self.assertEqual(data1["update_on"], Message.objects.get(id=1).update_on)
        self.assertEqual(data1["content"], Message.objects.get(id=1).content)
        self.assertEqual(1, Message.objects.get(id=1).token_id)

        delete2 = {"sender": self.user2.email, "tournament": self.tournament.id, "content": None, "update_on": 2}

        response = self.client.post(self.endpoint, delete2, format="json")

        self.assertEqual(6, Message.objects.count())
        self.assertEqual(delete2["sender"], Message.objects.get(id=6).sender.email)
        self.assertEqual(delete2["tournament"], Message.objects.get(id=6).chat.tournament.id)
        self.assertEqual(delete2["update_on"], Message.objects.get(id=6).update_on)
        self.assertEqual(delete2["content"], Message.objects.get(id=6).content)
        self.assertEqual(6, Message.objects.get(id=6).token_id)

        self.assertEqual(data2["sender"], Message.objects.get(id=2).sender.email)
        self.assertEqual(data2["tournament"], Message.objects.get(id=2).chat.tournament.id)
        self.assertEqual(data2["update_on"], Message.objects.get(id=2).update_on)
        self.assertEqual(data2["content"], Message.objects.get(id=2).content)
        self.assertEqual(2, Message.objects.get(id=2).token_id)


class UserTests(APITestCase):
    def test_user_get(self):
        user = UserFactory()

        list_url = reverse("api-user-list")
        detail_url = reverse("api-user-detail", kwargs={"pk": user.id})

        list_response = self.client.get(list_url)
        assert list_response.status_code == 200

        detail_response = self.client.get(detail_url)
        assert detail_response.status_code == 200

    def test_user_delete(self):
        user = UserFactory()

        url = reverse("api-user-detail", args=[user.id])
        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)
