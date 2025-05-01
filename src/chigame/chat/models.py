from django.db import models

from chigame.users.models import User


class LiveChat(models.Model):
    """
    Represents a new live chat between users.
    """

    # used to identify which channel the chat is on
    channel = models.TextField(unique=True, null=False)
    users = models.ManyToManyField(User, through="LiveChatUser", related_name="live_chats")

    def __str__(self):
        return f"LiveChat on channel:'{self.channel}')"


class LiveChatMessage(models.Model):
    """
    Represents a new message in the live chat.
    """

    live_chat_id = models.ForeignKey(LiveChat, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    message_content = models.TextField(null=False)

    def __str__(self):
        return f"Message: [{self.message_content}] by {self.user_id} in LiveChat {self.live_chat_id}"


class LiveChatUser(models.Model):
    """
    Represents a user mapped to a new live chat.
    """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    live_chat_id = models.ForeignKey(LiveChat, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_id} in chat {self.live_chat_id.channel}"
