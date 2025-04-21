# from django.test import TestCase

# Create your tests here.
# Compare this snippet from src/chigame/api/tests.py:
from django.urls import reverse

# Related third party imports
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils.serializer_helpers import ReturnDict

# Local application/library specific imports
from chigame.api.serializers import GameSerializer
from chigame.api.tests.factories import ChatFactory, GameFactory, TournamentFactory, UserFactory
from chigame.games.models import Game, Message, User


class GameTests(APITestCase):
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
