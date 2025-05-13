from django.urls import path

from . import views

urlpatterns = [
    path("<int:chat_id>/", views.chat, name="chat-page"),
    path("message/<int:message_id>/delete", views.delete_message, name="delete-message"),
]
