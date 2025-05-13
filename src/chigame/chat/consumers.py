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

    @database_sync_to_async
    def check_user_in_chat(self, user, chat):
        return chat.users.filter(id=user.id).exists()

    async def connect(self):
        """
        Connects to the chat room and adds the user who is connecting to the chat room to the group.
        """
        # Get chat_id from URL parameters
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_name = f"chat_{self.chat_id}"
        self.room_group_name = f"group_chat_{self.room_name}"

        # Get the authenticated user
        self.user = self.scope["user"]

        # Accept the connection first so we can send error messages
        await self.accept()

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "You must be logged in to join this chat"})
            )
            await self.close(code=4001)
            return

        # Get the chat and check if it exists
        self.live_chat = await self.get_live_chat(self.chat_id)
        if not self.live_chat:
            await self.send(text_data=json.dumps({"type": "error", "message": "Chat room does not exist"}))
            await self.close(code=4002)
            return

        # Check if user is a member of the chat
        is_member = await self.check_user_in_chat(self.user, self.live_chat)
        if not is_member:
            await self.send(text_data=json.dumps({"type": "error", "message": "You are not a member of this chat"}))
            await self.close(code=4003)
            return

        # Only add to group if all checks pass
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def disconnect(self, close_code):
        # Safely handle disconnect even if connection was never fully established
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

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
        msg_type = text_data_json.get("type", "send")
        if msg_type == "send":
            message = text_data_json["message"]
            user_id = text_data_json["user_id"]

            # Save message to database once when first received from client
            username = await self.save_message(self.chat_id, user_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "sendMessage",
                    "message": message,
                    "user_id": user_id,
                    "username": username,
                },
            )
        elif msg_type == "delete":
            message_id = text_data_json["message_id"]
            user_id = text_data_json["user_id"]

            try:
                # must need to call .delete() so you cant use message id
                msg = await database_sync_to_async(LiveChatMessage.objects.get)(id=message_id, user_id=user_id)
                await database_sync_to_async(msg.delete)()
                await self.channel_layer.group_send(
                    self.roomGroupName,
                    {"type": "deleteMessage", "message_id": message_id, "user_id": user_id},
                )
            except LiveChatMessage.DoesNotExist:
                print("error")

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

    async def deleteMessage(self, event):
        message_id = event["message_id"]
        user_id = event["user_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "delete",
                    "message": message_id,
                    "user_id": user_id,
                }
            )
        )
