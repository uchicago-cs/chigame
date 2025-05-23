from django.urls import path

from . import views

urlpatterns = [
    path("<int:chat_id>/", views.chat, name="chat-page"),
    path("live-chat-list/", views.live_chat_list, name="live-chat-list"),
    path("message/<int:message_id>/delete", views.delete_message, name="delete-message"),
    path("message/<int:message_id>/pin", views.pin_message, name="pin-message"),
    path("message/<int:message_id>/edit", views.edit_message, name="edit-message"),
    path("message/<int:message_id>/react", views.react_to_message, name="react-to-message"),
    path("toggle-profanity/", views.toggle_profanity, name="toggle-profanity"),
]
