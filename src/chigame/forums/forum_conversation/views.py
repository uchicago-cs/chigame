from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db.models import F, IntegerField, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from machina.apps.forum_conversation.views import TopicView as BaseTopicView
from machina.core.db.models import get_model

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

                # Create a new `Vote`
                post = Post.objects.filter(pk=liked_post).first()
                vote = Vote(rating=rating, post=post, poster=post.poster)
                vote.full_clean()
                vote.save()
            except (Post.DoesNotExist, ValidationError):
                print("An error occurred")
                pass

        return HttpResponseRedirect(self.request.path_info)

    def get_queryset(self):
        """Returns the list of items for this view."""
        self.topic = self.get_topic()
        qs = (
            self.topic.posts.all()
            .exclude(approved=False)
            .select_related("poster", "updated_by")
            .prefetch_related("attachments", "poster__forum_profile")
            .annotate(rating=Coalesce(Sum(F("vote__rating"), output_field=IntegerField()), 0))
        )

        return qs

    def get_context_data(self, **kwargs):
        # Get the posts associated with this topic
        topic = self.get_topic()
        posts = Post.objects.select_related("topic").filter(topic=topic)

        votes = Vote.objects.filter(post__in=posts)
        filtered_votes = defaultdict(int)

        for post in posts:
            filtered_votes[post] = 0

        for vote in votes:
            filtered_votes[vote.post] += vote.rating

        print(filtered_votes)

        return super().get_context_data(**kwargs)
