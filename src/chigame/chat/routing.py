from chat.consumers import ChatConsumer
from django.urls import path

websocket_urlpatterns = [
    path("", ChatConsumer.as_asgi()),
]
