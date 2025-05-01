import json

from channels.generic.websocket import AsyncWebsocketConsumer


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

    async def connect(self):
        # Use a default room name instead of getting it from URL parameters
        self.room_name = "default"
        self.roomGroupName = f"group_chat_{self.room_name}"
        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                "type": "sendMessage",
                "message": message,
                "username": username,
            },
        )

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps({"message": message, "username": username}))
