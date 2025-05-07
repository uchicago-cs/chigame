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

    Integration with Database Models:
    - LiveChat: Each WebSocket connection will be associated with a LiveChat
      instance identified by its unique channel name. The consumer will use the
      LiveChat's ID to route messages to the correct chat room.

    - LiveChatUser: When a user connects to a chat room, the system will check
      if there's an existing LiveChatUser record. If not, it will create one to
      track user participation in the chat. This allows tracking which users are
      in which chats.

    - LiveChatMessage: When a user sends a message through the WebSocket, the
      consumer will create a new LiveChatMessage record in the database, storing
      the message content, sender (User), timestamp, and the associated LiveChat.
      This provides message persistence and history.

    Message Flow:
    1. Client connects to WebSocket with chat ID in URL
    2. Consumer looks up corresponding LiveChat
    3. User is added to chat room group
    4. Messages sent to the group are persisted in LiveChatMessage
    5. New messages are broadcast to all connected clients in the same chat room
    """

    @database_sync_to_async
    def get_live_chat(self, chat_id):
        try:
            return LiveChat.objects.get(id=chat_id)
        except LiveChat.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, chat_id, user_id, message):
        chat = LiveChat.objects.get(id=chat_id)
        user = User.objects.get(id=user_id)

        # Save the message to the database
        LiveChatMessage.objects.create(live_chat=chat, user=user, content=message)

        # Return the display name (username or email)
        return user.username or user.email

    @database_sync_to_async
    def check_user_in_chat(self, user, chat):
        return chat.users.filter(id=user.id).exists()

    async def connect(self):
        # Initialize room attributes early
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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_id = text_data_json["user_id"]

        # Save message and get username
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

    async def sendMessage(self, event):
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
