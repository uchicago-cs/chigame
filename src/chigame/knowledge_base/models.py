from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
        User, on_delete=models.CASCADE, limit_choices_to={"moderator": True}
    )  # assume we delete this feedback if the reviewer deletes account
    comment = models.TextField(blank=True, null=True)
    guide_id = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="feedbacks")
    status = models.IntegerField(
        choices=[
            (Guide.GuideStatus.ACCEPTED, "Accepted"),
            (Guide.GuideStatus.REJECTED, "Rejected"),
            (Guide.GuideStatus.REQUESTED_CHANGE, "Requested Change"),
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    # make sure the status can display in text rather than in pk
    def get_status_display(self):
        status_map = {
            Guide.GuideStatus.ACCEPTED: "Accepted",
            Guide.GuideStatus.REJECTED: "Rejected",
            Guide.GuideStatus.REQUESTED_CHANGE: "Requested Change",
        }
        return status_map.get(self.status, "Invalid Status")


class GeneralFeedback(models.Model):
    feedback = models.TextField(_("Feedback"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("General Feedback")
        verbose_name_plural = _("General Feedback")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback from {self.created_at}"
