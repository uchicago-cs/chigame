import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chigame.users.models import User

from .models import LiveChat, LiveChatMessage

from .utils import ProfanityFilter


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

    async def connect(self):
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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_id = text_data_json["user_id"]
        
        # this will need to be made conditional at some point
        filtered_message = self.profanity_filter.censor_message(message)

        # Save message and get username
        username = await self.save_message(self.chat_id, user_id, message) # pass the original message

        # the filtered message is sent to the group - this is where the censorship happens
        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                "type": "sendMessage",
                "message": filtered_message,
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
