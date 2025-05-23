# from django.test import TestCase

# Create your tests here.
# Compare this snippet from src/chigame/api/tests.py:
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

# Related third party imports
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils.serializer_helpers import ReturnDict

# Local application/library specific imports
from chigame.api.serializers import GameSerializer
from chigame.api.tests.factories import (
    ChatFactory,
    FeedbackFactory,
    GameFactory,
    LobbyFactory,
    MatchFactory,
    TournamentFactory,
    UserFactory,
)
from chigame.games.models import Feedback, Game, Lobby, Message, Review, User


class GameTests(APITestCase):
    # for IF games migration resetting
    def setUp(self):
        super().setUp()
        Game.objects.all().delete()

    def check_equal(self, obj, expected: dict):
        """
        Helper function to check that the object data matches the expected data.
        """
        for key in expected:
            # Issue:  Serialized data often converts numbers to strings for transport
            # leading to a type mismatch when compared with their original Python types.

            # Solution: The check on lines 35-36 converts the serialized data to
            # the original Python type before comparing it with the expected data.
            # This ensures that the comparison is done on the same type of data.

            # For example, without this check, you might encounter issues
            # when comparing Decimal('5') and '5.00',
            # which would fail due to type mismatch despite representing the same value.

            if isinstance(obj, (ReturnDict, dict)):
                obj_value = obj[key]
            else:
                # Use getattr for object instances
                obj_value = getattr(obj, key, None)

            self.assertEqual(obj_value, expected[key])

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

    def test_get_game(self):
        """
        Ensure we can get a game object.
        """

        # Create a game object
        game = GameFactory()

        # Get the game object
        url = reverse("api-game-list")
        response = self.client.get(url, format="json")
        serialized_game = GameSerializer(game).data

        # Check that the game object was retrieved correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Game.objects.count(), 1)
        self.check_equal(serialized_game, response.data["results"][0])

    def test_get_game_list1(self):
        """
        Ensure we can get a list of game objects.
        """

        # create three game objects
        game1 = GameFactory()
        game2 = GameFactory()
        game3 = GameFactory()

        # Get the game object list
        url = reverse("api-game-list")
        response = self.client.get(url, format="json")

        # Check that the game object list was retrieved correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test that the game object list contains the two game objects we created
        self.assertEqual(Game.objects.count(), 3)
        serialized_game1 = GameSerializer(game1).data
        serialized_game2 = GameSerializer(game2).data
        serialized_game3 = GameSerializer(game3).data

        self.check_equal(serialized_game1, response.data["results"][0])
        self.check_equal(serialized_game2, response.data["results"][1])
        self.check_equal(serialized_game3, response.data["results"][2])

    def test_game_list2(self):
        """
        Ensure we can get a list of game objects.
        """
        url = reverse("api-game-list")

        # create four game objects
        game1 = GameFactory()
        game2 = GameFactory()
        game3 = GameFactory()
        game4 = GameFactory()

        # Get the game object list
        url = reverse("api-game-list")
        response = self.client.get(url, format="json")

        # Check that the game object list was retrieved correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serialized_game1 = GameSerializer(game1).data
        serialized_game2 = GameSerializer(game2).data
        serialized_game3 = GameSerializer(game3).data
        serialized_game4 = GameSerializer(game4).data

        # test that the game object list contains the two game objects we created
        self.check_equal(serialized_game1, response.data["results"][0])
        self.check_equal(serialized_game2, response.data["results"][1])
        self.check_equal(serialized_game3, response.data["results"][2])
        self.check_equal(serialized_game4, response.data["results"][3])

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

    def test_game_list_pagination_metadata(self):
        """
        Ensure paginated metadata is returned for the /api/games/ endpoint.
        """
        for _ in range(15):
            GameFactory()

        url = reverse("api-game-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertLessEqual(len(response.data["results"]), 10)


class ChatTests(APITestCase):
    def test_create_message(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.game = GameFactory()
        self.tournament = TournamentFactory(game=self.game)
        self.chat = ChatFactory(tournament=self.tournament)
        self.endpoint = reverse("api-chat-list")

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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
        detail_url = reverse("api-user-detail", kwargs={"slug": user.username})

        list_response = self.client.get(list_url)
        assert list_response.status_code == 200

        detail_response = self.client.get(detail_url)
        assert detail_response.status_code == 200

    def test_user_delete(self):
        user = UserFactory()
        self.assertEqual(User.objects.count(), 1)

        url = reverse("api-user-detail", args=[user.username])
        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_user_post(self):
        user = {
            "email": "user@example.com",
            "name": "John Doe",
            "username": "john_doe",
            "password": "password",
            "tokens": 2,
        }

        url = reverse("api-user-list")
        response = self.client.post(url, data=user, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data["email"], user["email"])
        self.assertEqual(response.data["name"], user["name"])

    def test_user_patch(self):
        user = UserFactory()
        url = reverse("api-user-detail", kwargs={"slug": user.username})

        updated_data = {"username": "Johnn"}

        response = self.client.patch(url, data=updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data["username"], updated_data["username"])

    def test_feed_message(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.game = GameFactory()
        self.tournament = TournamentFactory(game=self.game)
        self.chat = ChatFactory(tournament=self.tournament)
        self.endpoint = reverse("api-chat-list")

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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

        self.client.force_authenticate(user=self.user1)
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

        self.client.force_authenticate(user=self.user2)
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

        self.client.force_authenticate(user=self.user1)
        feed1 = {"token_id": 0, "tournament": self.tournament.id}

        response = self.client.post(reverse("api-chat-detail"), feed1, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data[0]["content"], data1["content"])
        self.assertEqual(response.data[1]["content"], data2["content"])
        self.assertEqual(response.data[2]["content"], data3["content"])
        self.assertEqual(response.data[3]["content"], data4["content"])
        self.assertEqual(response.data[4]["content"], delete1["content"])
        self.assertEqual(response.data[5]["content"], delete2["content"])
        self.assertEqual(response.data[0]["token_id"], 1)
        self.assertEqual(response.data[1]["token_id"], 2)
        self.assertEqual(response.data[2]["token_id"], 3)
        self.assertEqual(response.data[3]["token_id"], 4)
        self.assertEqual(response.data[4]["token_id"], 5)
        self.assertEqual(response.data[5]["token_id"], 6)
        self.assertEqual(response.data[0]["sender"], Message.objects.get(id=1).sender.name)
        self.assertEqual(response.data[1]["sender"], Message.objects.get(id=2).sender.name)
        self.assertEqual(response.data[2]["sender"], Message.objects.get(id=3).sender.name)
        self.assertEqual(response.data[3]["sender"], Message.objects.get(id=4).sender.name)
        self.assertEqual(response.data[4]["sender"], Message.objects.get(id=5).sender.name)
        self.assertEqual(response.data[5]["sender"], Message.objects.get(id=6).sender.name)
        self.assertEqual(response.data[0]["update_on"], data1["update_on"])
        self.assertEqual(response.data[1]["update_on"], data2["update_on"])
        self.assertEqual(response.data[2]["update_on"], data3["update_on"])
        self.assertEqual(response.data[3]["update_on"], data4["update_on"])
        self.assertEqual(response.data[4]["update_on"], delete1["update_on"])
        self.assertEqual(response.data[5]["update_on"], delete2["update_on"])


class LobbyTests(APITestCase):
    """
    Test cases for Lobby API Endpoints.
    """

    def test_get_lobby(self):
        """
        Ensure we can get a lobby object.
        """

        # Create a lobby object
        lobby = LobbyFactory()

        # Get the lobby object
        url = reverse("api-lobby-detail", args=[lobby.id])
        response = self.client.get(url, format="json")

        # Check that the lobby object was retrieved correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Lobby.objects.count(), 1)
        self.assertEqual(response.data["id"], lobby.id)
        self.assertEqual(response.data["name"], lobby.name)
        self.assertEqual(response.data["game"], lobby.game.id)
        self.assertEqual(response.data["game_mod_status"], lobby.game_mod_status)
        self.assertEqual(response.data["created_by"], lobby.created_by.id)
        self.assertEqual(response.data["min_players"], lobby.min_players)
        self.assertEqual(response.data["max_players"], lobby.max_players)
        self.assertEqual(response.data["time_constraint"], lobby.time_constraint)

    def test_delete_lobby(self):
        """
        Ensure we can delete a game object.
        """

        # Create a lobby object
        user = UserFactory()
        self.client.force_authenticate(user=user)
        lobby = LobbyFactory(created_by=user)

        # Delete the lobby object
        url = reverse("api-lobby-detail", args=[lobby.id])
        response = self.client.delete(url, format="json")

        # Check that the lobby object was deleted correctly
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lobby.objects.count(), 0)

    def test_delete_lobby_unauthorized(self):
        """
        Ensure we cannot delete a lobby object if the user is not the creator of the lobby.
        """

        # Create a lobby object
        lobby = LobbyFactory()

        # Create user who creates the lobby and another user
        creator = UserFactory()
        other_user = UserFactory()
        lobby.created_by = creator
        lobby.save()
        self.client.force_authenticate(user=other_user)

        # Delete the lobby object
        url = reverse("api-lobby-detail", args=[lobby.id])
        response = self.client.delete(url, format="json")

        # Check lobby not deleted
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lobby.objects.count(), 1)
        self.assertEqual(Lobby.objects.get(id=lobby.id).created_by, creator)

    def test_patch_lobby_authorized(self):
        """
        Ensure we can patch a lobby object if the user is the creator of the lobby.
        """
        # Create a lobby object
        user = UserFactory()
        self.client.force_authenticate(user=user)
        lobby = LobbyFactory(created_by=user)

        # Update data
        updated_data = {
            "name": "Updated Lobby Name",
            "min_players": 3,
            "max_players": 6,
        }

        # Patch request
        url = reverse("api-lobby-detail", args=[lobby.id])
        response = self.client.patch(url, updated_data, format="json")

        # Check that the lobby object was patched correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], updated_data["name"])
        self.assertEqual(response.data["min_players"], updated_data["min_players"])
        self.assertEqual(response.data["max_players"], updated_data["max_players"])

        # Check that database was updated

        updated_lobby = Lobby.objects.get(id=lobby.id)
        self.assertEqual(updated_lobby.name, updated_data["name"])
        self.assertEqual(updated_lobby.min_players, updated_data["min_players"])
        self.assertEqual(updated_lobby.max_players, updated_data["max_players"])

    def test_patch_lobby_unauthorized(self):
        """
        Ensure we cannot patch a lobby object if the user is not the creator of the lobby.
        """

        # Create a lobby object
        lobby = LobbyFactory()

        # Create user who creates the lobby and another user
        creator = UserFactory()
        other_user = UserFactory()
        lobby.created_by = creator
        lobby.save()
        self.client.force_authenticate(user=other_user)

        # Update data
        updated_data = {
            "name": "Updated Lobby Name",
            "min_players": 3,
            "max_players": 6,
        }

        # Patch request
        url = reverse("api-lobby-detail", args=[lobby.id])
        response = self.client.patch(url, updated_data, format="json")

        # Check that the lobby object was patched correctly
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check database not updated
        unchanged_lobby = Lobby.objects.get(id=lobby.id)
        self.assertEqual(unchanged_lobby.name, lobby.name)


class AccessControlTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.game = GameFactory()

    def test_authenticated_user_can_post_lobby(self):
        url = reverse("api-lobby-list")
        data = {
            "game": self.game.id,
            "name": "New Lobby",
            "min_players": 2,
            "max_players": 6,
            "members": [self.user.id],
            "created_by": self.user.id,
        }
        response = self.client.post(url, data, format="json")

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cannot_post_lobby(self):
        self.client.logout()
        url = reverse("api-lobby-list")
        data = {
            "game": self.game.id,
            "name": "Fail Lobby",
            "min_players": 2,
            "max_players": 6,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_post_game(self):
        self.client.logout()
        url = reverse("api-game-list")
        data = {"name": "Uno", "max_players": 4}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_post_message(self):
        tournament = TournamentFactory(game=self.game)
        chat = ChatFactory(tournament=tournament)  # noqa: F841
        url = reverse("api-chat-list")
        data = {
            "sender": self.user.email,
            "tournament": tournament.id,
            "content": "Hello from an authenticated user",
            "update_on": None,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cannot_post_message(self):
        self.client.logout()
        tournament = TournamentFactory(game=self.game)
        # chat = ChatFactory(tournament=tournament)
        url = reverse("api-chat-list")
        data = {
            "tournament": tournament.id,
            "content": "This should fail",
            "update_on": None,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_fetch_message_feed(self):
        tournament = TournamentFactory(game=self.game)
        ChatFactory(tournament=tournament)
        url = reverse("api-chat-detail")
        data = {"token_id": 0, "tournament": tournament.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_fetch_message_feed(self):
        self.client.logout()
        tournament = TournamentFactory(game=self.game)
        ChatFactory(tournament=tournament)
        url = reverse("api-chat-detail")
        data = {"token_id": 0, "tournament": tournament.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SpamFilterTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.game = GameFactory()
        self.game.save()
        self.tournament = TournamentFactory(game=self.game)
        self.chat = ChatFactory(tournament=self.tournament)
        self.client.force_authenticate(user=self.user)

    def test_review_rejects_spam(self):
        url = reverse("api-game-review-create", args=[self.game.id])
        data = {
            "title": "Limited offer",
            "review": "Buy now and save big",  # Spammy content
            "rating": 1,
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("spam", str(response.data).lower())
        self.assertEqual(Review.objects.count(), 0)

    # def test_message_rejects_spam(self):
    #     url = reverse("api-chat-list")
    #     data = {
    #         # "sender": self.user.email,
    #         "tournament": self.tournament.id,
    #         "content": "Click here to claim free money!",  # Spammy content
    #         "update_on": None,
    #     }
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("spam", str(response.data).lower())
    #     self.assertEqual(Message.objects.count(), 0)

    def test_review_allows_normal_content(self):
        url = reverse("api-game-review-create", args=[self.game.id])

        print("Game ID:", self.game.id)
        from chigame.games.models import Game  # add this import at the top if needed

        print("Game exists:", Game.objects.filter(id=self.game.id).exists())

        data = {
            "title": "Challenging and fun",
            "review": "Had a great time playing with friends.",
            "rating": 5,
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    # def test_message_with_excessive_exclamations_rejected(self):
    #     url = reverse("api-chat-list")
    #     data = {
    #         # "sender": self.user.email,
    #         "tournament": self.tournament.id,
    #         "content": "!!!!!!!!!!!!!!!",  # Spam-like behavior
    #         "update_on": None,
    #     }
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("spam", str(response.data).lower())
    #     self.assertEqual(Message.objects.count(), 0)

    def test_review_with_excessive_characters_rejected(self):
        url = reverse("api-game-review-create", args=[self.game.id])
        data = {
            "title": "Spammy symbols",
            "review": "!!!!!!!!!",  # Detected by repeated character rule
            "rating": 1,
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("spam", str(response.data).lower())
        self.assertEqual(Review.objects.count(), 0)

    def test_short_legit_review_passes(self):
        url = reverse("api-game-review-create", args=[self.game.id])
        data = {
            "title": "Fun!",
            "review": "Quick and intense game",  # short but varied
            "rating": 4,
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_review_with_repetitive_words_rejected(self):
        url = reverse("api-game-review-create", args=[self.game.id])
        data = {
            "title": "meh",
            "review": "good good good",  # Not enough unique words
            "rating": 3,
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("spam", str(response.data).lower())
        self.assertEqual(Review.objects.count(), 0)

    def test_review_too_short_rejected(self):
        url = reverse("api-game-review-create", args=[self.game.id])
        data = {
            "title": "Too short",
            "review": "ab",  # Only two characters
            "rating": 2,
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("spam", str(response.data).lower())
        self.assertEqual(Review.objects.count(), 0)


class SimulationTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.game = GameFactory()
        self.tournament = TournamentFactory(game=self.game, created_by=self.user)

        self.matches = []
        # Create 4 matches that are properly wired to this tournament + game
        for _ in range(4):
            players = UserFactory.create_batch(2)
            lobby = LobbyFactory(game=self.game, created_by=self.user)
            lobby.members.set(players)
            lobby.save()

            match = MatchFactory(game=self.game, lobby=lobby, players=players)
            self.tournament.matches.add(match)
            self.matches.append(match)
        # # create 4 matches under that tournament
        # for _ in range(4):
        #     m = MatchFactory()
        #     self.tournament.matches.add(m)

        self.url = reverse("api-tournament-simulate", args=[self.tournament.pk])
        self.client.force_authenticate(self.user)

    def test_single_elimination(self):
        # Simulate a tournament with single elimination
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_double_elimination"])
        self.assertIn("rounds", resp.data)
        # the winner must be one of the players in your matches
        all_player_ids = {u.id for m in self.tournament.matches.all() for u in m.players.all()}
        self.assertIn(resp.data["tournament_winner"], all_player_ids)

    def test_double_elimination(self):
        # Simulate a tournament with double elimination
        resp = self.client.post(self.url, {"double_elimination": True}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["is_double_elimination"])

    def test_simulation_with_no_matches(self):
        # Simulate a tournament with no matches (edge case)

        # Remove all matches from tournament
        self.tournament.matches.clear()

        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["rounds"], {})
        self.assertIsNone(resp.data["tournament_winner"])

    def test_simulated_round_match_counts(self):
        # Ensures that the number of matches in the first round is equal to the number of matches in the tournament
        # This prevents duplicate mathces
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, 200)

        rounds = resp.data["rounds"]
        round1_matches = rounds[1]["winners"]
        self.assertEqual(len(round1_matches), self.tournament.matches.count())

    def test_double_elimination_includes_losers_bracket(self):
        resp = self.client.post(self.url, {"double_elimination": True}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("losers", resp.data["rounds"][2])

    def test_double_elimination_final_match_present(self):
        # Checks that double elimination includes a final match
        resp = self.client.post(self.url, {"double_elimination": True}, format="json")
        self.assertEqual(resp.status_code, 200)

        final_matches = resp.data["rounds"].get("3", {}).get("final", [])
        if len(final_matches) > 0:
            self.assertIn("players", final_matches[0])


class FeedbackTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.game = GameFactory()

        now = timezone.now()

        self.tournament = TournamentFactory(
            game=self.game,
            created_by=self.user,
            registration_start_date=now + timedelta(days=1),
            registration_end_date=now + timedelta(days=2),
            tournament_start_date=now + timedelta(days=3),
            tournament_end_date=now + timedelta(days=4),
        )

        # self.tournament = TournamentFactory(game=self.game, created_by=self.user)
        self.endpoint = reverse("api-feedback-list-create", args=[self.tournament.id])
        self.client.force_authenticate(user=self.user)

    def test_create_feedback(self):
        self.client.force_authenticate(user=self.user)

        data = {"rating": 5, "comment": "Awesome tournament!"}
        response = self.client.post(self.endpoint, data, format="json")

        print(response.status_code)
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["rating"], data["rating"])
        self.assertEqual(response.data["comment"], data["comment"])
        self.assertEqual(response.data["tournament"], self.tournament.id)
        self.assertEqual(response.data["user"], self.user.id)

    def test_list_feedback_ordering(self):
        FeedbackFactory(tournament=self.tournament, user=self.user, rating=3, comment="First comment")
        FeedbackFactory(tournament=self.tournament, user=self.user, rating=4, comment="Second comment")

        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        # Check reverse chronological order by created_at
        self.assertGreaterEqual(results[0]["created_at"], results[1]["created_at"])

    def test_update_feedback(self):
        feedback = FeedbackFactory(tournament=self.tournament, user=self.user, rating=2)
        detail_url = reverse("api-feedback-detail", args=[feedback.id])

        data = {"rating": 4, "comment": "Updated comment"}

        response = self.client.patch(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(response.data["comment"], "Updated comment")

    def test_delete_feedback(self):
        feedback = FeedbackFactory(tournament=self.tournament, user=self.user, rating=2)
        detail_url = reverse("api-feedback-detail", args=[feedback.id])

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Feedback.objects.filter(id=feedback.id).exists())


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword123")
        self.token_url = reverse("token-obtain-pair")

        # we use lobby since it requries authorization
        self.game = GameFactory()
        self.protected_url = reverse("api-lobby-list")
        self.protected_data = {
            "game": self.game.id,
            "name": "New Lobby",
            "min_players": 2,
            "max_players": 4,
            "members": [self.user.id],
            "created_by": self.user.id,
        }

    def test_obtain_token(self):
        response = self.client.post(
            self.token_url, {"username": "testuser", "password": "testpassword123"}, format="json"  # try username
        )

        # if username doesn't work us e email
        if response.status_code != status.HTTP_200_OK:
            response = self.client.post(
                self.token_url, {"email": "test@example.com", "password": "testpassword123"}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        return response.data["access"], response.data["refresh"]

    def test_access_protected_endpoint_with_token(self):
        try:
            access_token, _ = self.test_obtain_token()
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
            response = self.client.post(self.protected_url, self.protected_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        except AssertionError as e:
            self.fail(f"Failed to access protected endpoint: {e}")

    def test_token_refresh(self):
        try:
            _, refresh_token = self.test_obtain_token()

            # se refresh token to get new access token
            refresh_url = reverse("token-refresh")
            refresh_response = self.client.post(refresh_url, {"refresh": refresh_token}, format="json")

            self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
            self.assertIn("access", refresh_response.data)
        except AssertionError as e:
            self.fail(f"Failed to refresh token: {e}")

    def test_endpoint_rejects_unauthenticated_requests(self):
        # dont' set credentials
        response = self.client.post(self.protected_url, self.protected_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_endpoint_rejects_malformed_token(self):
        # set a malformed token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token_string")
        response = self.client.post(self.protected_url, self.protected_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
