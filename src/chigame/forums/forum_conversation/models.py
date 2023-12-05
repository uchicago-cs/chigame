from django.conf import settings
from django.db import models
from machina.apps.forum_conversation.abstract_models import AbstractPost

from chigame.users.models import User


class Post(AbstractPost):
    # Each post may be liked or disliked
    ratings = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Vote",
        related_name="ratings",
        editable=False,
        blank=True,
    )


class Vote(models.Model):
    class Rating(models.IntegerChoices):
        LIKE = 1, "Like"
        DISLIKE = -1, "Dislike"

    poster = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(choices=Rating.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["poster", "post"], name="unique_rating")]


from machina.apps.forum_conversation.models import *  # noqa
