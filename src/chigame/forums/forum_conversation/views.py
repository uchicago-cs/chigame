from django.core.exceptions import ValidationError
from django.db.models import Case, F, IntegerField, Sum, When
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from machina.apps.forum_conversation.views import TopicView as BaseTopicView
from machina.core.db.models import get_model
from rest_framework import status

from .models import Vote

Post = get_model("forum_conversation", "Post")


class TopicView(BaseTopicView):
    def post(self, request, **kwargs):
        """Handles POST requests."""

        # Retrieve the liked post
        liked_post = request.POST.get("post_id", None)
        if liked_post:
            try:
                assert liked_post.isdigit()
                vote_value = request.POST.get("rate")

                if vote_value == "like":
                    rating = 1
                elif vote_value == "dislike":
                    rating = -1
                else:
                    raise ValidationError

                post = Post.objects.filter(pk=liked_post).first()
                vote = Vote.objects.get(rating=rating, post=post, poster=post.poster)

                # Remove the vote if it existed previously
                vote.delete()
            except Vote.DoesNotExist:
                Vote.objects.filter(post=post, poster=post.poster).delete()

                # Create a new `Vote`
                vote = Vote.objects.create(rating=rating, post=post, poster=post.poster)
                vote.full_clean()
                vote.save()
                return HttpResponse(status=status.HTTP_201_CREATED)
            except (Post.DoesNotExist, ValidationError):
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """Returns the list of items for this view."""
        self.topic = self.get_topic()
        qs = (
            self.topic.posts.all()
            .exclude(approved=False)
            .select_related("poster", "updated_by")
            .prefetch_related("attachments", "poster__forum_profile")
            .annotate(
                rating=Coalesce(Sum(F("vote__rating"), output_field=IntegerField()), 0),
                user_rating=Coalesce(
                    Case(
                        When(vote__poster=self.request.user, then=F("vote__rating")),
                        default=0,
                        output_field=IntegerField(),
                    ),
                    0,
                ),
            )
        )

        return qs
