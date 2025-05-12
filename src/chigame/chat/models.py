from django.db import models

from chigame.users.models import User


class LiveChat(models.Model):
    """
    Represents a new live chat between users.
    """

    name = models.TextField(null=False)
    users: models.ManyToManyField = models.ManyToManyField(User, through="LiveChatUser", related_name="live_chats")

    def __str__(self):
        return f"LiveChat with name:'{self.name}'"


class LiveChatMessage(models.Model):
    """
    A message in a live chat.
    """

    live_chat = models.ForeignKey(LiveChat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=False)

    def __str__(self):
        return f"Message: [{self.content}] by {self.user} in LiveChat {self.live_chat}"


class LiveChatUser(models.Model):
    """
    A user in a live chat.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    live_chat = models.ForeignKey(LiveChat, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} in chat {self.live_chat.name}"


class LiveChatMessageReaction(models.Model):
    """
    A reaction to a LiveChatMessage.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(LiveChatMessage, on_delete=models.CASCADE)
    content = models.CharField(null=False, max_length=10)

    class Meta:
        unique_together = ("user", "message", "content")

    def __str__(self):
        return f"{self.user} reacted with {self.content} to message {self.message}"
