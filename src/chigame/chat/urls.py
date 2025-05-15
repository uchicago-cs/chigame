from django.urls import path

from . import views

urlpatterns = [
    path("<int:chat_id>/", views.chat, name="chat-page"),
    path("live-chat-list/", views.live_chat_list, name="live-chat-list"),
    path("live-chat-list/create/", views.create_live_chat, name="create-live-chat"),
]
