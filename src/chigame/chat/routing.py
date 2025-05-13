from django.urls import path

from chigame.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi()),  # chat_id is used as the channel name
]
