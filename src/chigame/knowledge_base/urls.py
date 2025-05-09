from django.urls import path

from .views import ContributorView, DefaultView, ModeratorGuidesPending

urlpatterns = [
    path("", DefaultView, name="knowledge-base"),
    path("moderation", ModeratorGuidesPending.as_view(), name="knowledge-base-moderator"),
    path("contribution", ContributorView, name="knowledge-base-contributor"),
]

# Eventually, we should add '!<slug:username>' the contribution path so we can
# list all the guides associated with the current user
