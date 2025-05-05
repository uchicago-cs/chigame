from django.db import models
from django.utils import timezone

from chigame.games.models import Game

# Create your models here.
from chigame.users.models import User


# record the uploaded guides
# If a guide is requested change and a new ver is uploaded, this will modify
# the existing Guide object rather than creating a new Guide object.
class Guide(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_guides"
    )  # assume we delete this guide if author deletes account
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    content = models.TextField()
    recent_upload = models.DateTimeField(auto_now_add=True)

    class GuideStatus(models.IntegerChoices):
        PENDING = 0, "Pending"
        ACCEPTED = 1, "Accepted"
        REJECTED = 2, "Rejected"
        REQUESTED_CHANGE = 3, "Requested Change"

    status = models.IntegerField(
        choices=GuideStatus.choices,
        default=GuideStatus.PENDING,
    )

    # record user likes and favorites
    likes = models.ManyToManyField(User, blank=True, related_name="liked_guides")
    favorites = models.ManyToManyField(User, blank=True, related_name="favorite_guides")

    # manually save the guide object, to update the timestamp if and only if
    # the content field is updated (didn't use auto_now = True, because the
    # status could be updated at a review feedback, but we want to save the
    # recentest upload time)
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # This is an existing object (not a new one)
            old = Guide.objects.get(pk=self.pk)
            if old.content != self.content:
                self.recent_upload = timezone.now()
        super().save(*args, **kwargs)


# record each piece of review feedback that a moderator provides
# the same guide request can have multiple entries of ReviewFeedback (if a guide
#  is first requested change, then approved, this will be stored as two separate
# ReviewFeedback objects)
class ReviewFeedback(models.Model):
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # assume we delete this feedback if the reviewer deletes account
    comment = models.TextField(blank=True, null=True)
    guide_id = models.ForeignKey(Guide, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=[
            (Guide.GuideStatus.ACCEPTED, "Accepted"),
            (Guide.GuideStatus.REJECTED, "Rejected"),
            (Guide.GuideStatus.REQUESTED_CHANGE, "Requested Change"),
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
