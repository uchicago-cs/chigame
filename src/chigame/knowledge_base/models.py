from django.db import models
from django.utils import timezone

from chigame.games.models import Game

# Create your models here.
from chigame.users.models import User


class GuideStatus(models.IntegerChoices):
    PENDING = 0, "Pending"
    ACCEPTED = 1, "Accepted"
    REJECTED = 2, "Rejected"
    REQUESTED_CHANGE = 3, "Requested Change"


# record the uploaded guides
# If a guide is requested change and a new ver is uploaded, this will modify
# the existing Guide object rather than creating a new Guide object.
class Guide(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # should we delete the guide if the author deletes their account?
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    content = models.TextField()
    recent_upload = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=GuideStatus.choices,
        default=GuideStatus.PENDING,
    )
    n_likes = models.IntegerField(default=0)

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
    )  # should we delete the guide if the reviewer deletes their account?
    comment = models.TextField(blank=True, null=True)
    guide_id = models.ForeignKey(Guide, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=[
            (GuideStatus.ACCEPTED, "Accepted"),
            (GuideStatus.REJECTED, "Rejected"),
            (GuideStatus.REQUESTED_CHANGE, "Requested Change"),
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)


# track when a user add a guide to their "favorite"
class Favorite(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    guide_id = models.ForeignKey(Guide, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user_id", "guide_id"]


# track when a user "likes" a guide
class Like(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    guide_id = models.ForeignKey(Guide, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user_id", "guide_id"]
