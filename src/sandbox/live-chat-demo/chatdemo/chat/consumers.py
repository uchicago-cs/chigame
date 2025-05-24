import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    This is a simple chat consumer that sends and receives messages to and from the group.
    """

    async def connect(self):
        """
        This is called when the client connects to the WebSocket.
        """
        self.roomGroupName = "group_chat_gfg"
        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnects the client from the group.

        Args:
            close_code (int): The close code of the connection.
        """
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_name)

    async def receive(self, text_data):
        """
        Receives a message from the client and sends it to the group.

        Args:
            text_data (str): The message from the client.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]

        # this is the file we modify in the chat app to add things such as profanity filters, etc.

        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                "type": "sendMessage",
                "message": message,
                "username": username,
            },
        )

    async def sendMessage(self, event):
        """
        Sends a message to the client.

        Args:
            event (dict): The event from the group.
        """
        message = event["message"]
        username = event["username"]

        await self.send(text_data=json.dumps({"message": message, "username": username}))
