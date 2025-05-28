import asyncio
import json
import re

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from chigame.users.models import User

from .models import LiveChat, LiveChatMessage, LiveChatUser
from .utils import ProfanityFilter

# Rate limiting constants
MESSAGES_PER_SECOND = 1  # Maximum messages allowed per second
RATE_LIMIT_WINDOW_SECONDS = 1  # Time window for rate limiting in seconds
RATE_LIMIT_KEY_PREFIX = "chat_rate_limit:"


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
                "message": filtered_message,
                "user_id": user_id,
                "username": username,
                "message_id": message_id,
                "reply_to": reply_to_id,
                "reply_to_username": reply_to_username,
                "reply_to_content": reply_to_content,
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
