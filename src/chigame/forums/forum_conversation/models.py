from django.db import models


class Vote(models.Model):
    class Rating(models.IntegerChoices):
        LIKE = 1, "Like"
        DISLIKE = -1, "Dislike"

    rating = models.IntegerField(choices=Rating.choices)


from machina.apps.forum_conversation.models import *  # noqa
