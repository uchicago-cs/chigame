from django.db import models

from chigame.users.models import User


class LiveChat(models.Model):
    """
    Represents a new live chat between users.
    """

    channel = models.TextField(unique=True, null=False)
    users: models.ManyToManyField = models.ManyToManyField(User, through="LiveChatUser", related_name="live_chats")

    def __str__(self):
        return f"LiveChat on channel:'{self.channel}')"


class LiveChatMessage(models.Model):
    """
    A message in a live chat.
    """

    live_chat_id = models.ForeignKey(LiveChat, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=False)

    def __str__(self):
        return f"Message: [{self.content}] by {self.user_id} in LiveChat {self.live_chat_id}"


class LiveChatUser(models.Model):
    """
    A user in a live chat.
    """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    live_chat_id = models.ForeignKey(LiveChat, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_id} in chat {self.live_chat_id.channel}"
