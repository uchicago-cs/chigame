from django.db import models

from chigame.users.models import User

MAX_EMOJI_LENGTH = 10


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
    An emoji reaction to a LiveChatMessage.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(LiveChatMessage, on_delete=models.CASCADE)

    # this is the emoji that the user reacted with
    content = models.CharField(
        null=False, max_length=MAX_EMOJI_LENGTH, help_text=f"Up to {MAX_EMOJI_LENGTH} emoji characters"
    )

    class Meta:
        unique_together = ("user", "message", "content")

    def __str__(self):
        return f"{self.user} reacted with {self.content} to message {self.message}"


class LiveChatPollOption(models.Model):
    """
    An option in a LiveChatPoll.
    """

    content = models.TextField(null=False)


class LiveChatPoll(models.Model):
    """
    A poll in a live chat.
    """

    live_chat = models.ForeignKey(LiveChat, on_delete=models.CASCADE)
    question = models.TextField(null=False)
    options = models.ManyToManyField(LiveChatPollOption, related_name="polls")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # if the current date is after the closed_at date, the poll is closed
    # this is used to determine if the poll is still active
    closed_at = models.DateTimeField(null=True, help_text="The date and time the poll will be closed")
    # if the closed_at is null, the poll can be active indefinitely

    def __str__(self):
        return f"Poll: {self.question} in LiveChat {self.live_chat}"


class LiveChatPollVote(models.Model):
    """
    A vote in a LiveChatPoll.
    """

    poll = models.ForeignKey(LiveChatPoll, on_delete=models.CASCADE)
    option = models.ForeignKey(LiveChatPollOption, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "option", "user"], name="unique_poll_option_user")
        ]
    def __str__(self):
        return f"{self.user} voted for {self.option} in Poll {self.poll}"
