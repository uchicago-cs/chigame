import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chigame.users.models import User

from .models import LiveChat, LiveChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    """
    ChatConsumer is a WebSocket consumer that handles chat functionality.
    It allows users to connect to a chat room and send messages to other users
    in the room.
    """

    @database_sync_to_async
    def get_live_chat(self, chat_id):
        """
        Gets the live chat from the database.

        Args:
            chat_id (int): The ID of the chat.

        Returns:
            LiveChat: The live chat object.
        """
        try:
            return LiveChat.objects.get(id=chat_id)
        except LiveChat.DoesNotExist:
            return None

    async def connect(self):
        """
        Connects to the chat room and adds the user who is connecting to the chat room to the group.
        """
        # Get chat_id from URL parameters
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.live_chat = await self.get_live_chat(self.chat_id)

        if not self.live_chat:
            await self.close()
            return

        self.room_name = f"chat_{self.chat_id}"
        self.roomGroupName = f"group_chat_{self.room_name}"

        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_name)

    @database_sync_to_async
    def save_message(self, chat_id, user_id, message):
        """
        Saves the message to the database. This is called when a message is received from the client.

        Args:
            chat_id (int): The ID of the chat.
            user_id (int): The ID of the user.
            message (str): The message to save.
        """
        chat = LiveChat.objects.get(id=chat_id)
        user = User.objects.get(id=user_id)

        # Save the message to the database
        LiveChatMessage.objects.create(live_chat=chat, user=user, content=message)

        # Return the display name (username or email)
        return user.username or user.email

    async def receive(self, text_data):
        """
        Receives messages from the client, saves them to the database once,
        and broadcasts to all connected clients.

        Args:
            text_data (str): The message data received from the client.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_id = text_data_json["user_id"]

        # Save message to database once when first received from client
        username = await self.save_message(self.chat_id, user_id, message)

        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                "type": "sendMessage",
                "message": message,
                "user_id": user_id,
                "username": username,
            },
        )

    async def sendMessage(self, event):
        """
        Broadcasts received messages to clients without saving to database again.
        The message has already been saved once when initially received.

        Args:
            event (dict): The event data containing message details.
        """
        message = event["message"]
        user_id = event["user_id"]
        username = event.get("username", "")

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "user_id": user_id,
                    "username": username,
                }
            )
        )
