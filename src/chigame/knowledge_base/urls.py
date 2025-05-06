from django.urls import path

from .views import ContributorView, DefaultView, ModeratorGuidesPending

urlpatterns = [
    path("", DefaultView, name="knowledge-base"),
    path("moderation", ModeratorGuidesPending, name="knowledge-base-moderator"),
    path("contribution", ContributorView, name="knowledge-base-contributor"),
]
