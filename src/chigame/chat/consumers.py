import json
import re

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chigame.users.models import User

from .models import LiveChat, LiveChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    # ... existing connect, disconnect, save_message, etc. ...

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        user_id = data.get("user_id")

        # 1) Save the message to DB
        username = await self.save_message(self.chat_id, user_id, message)

        # 2) Skeleton: detect URLs and broadcast an `unfurl` event
        urls = re.findall(r"https?://[^\s]+", message)
        if urls:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "sendUnfurl",
                    "urls": urls,
                },
            )

        # 3) Broadcast the original message
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
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "user_id": event["user_id"],
                    "username": event.get("username", ""),
                }
            )
        )

    async def sendUnfurl(self, event):
        # send minimal unfurl placeholder
        await self.send(
            text_data=json.dumps(
                {
                    "type": "unfurl",
                    "urls": event["urls"],
                }
            )
        )
