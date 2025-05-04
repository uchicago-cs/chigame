from django.urls import path

from .views import ContributorView, DefaultView, ModeratorView

urlpatterns = [
    path("", DefaultView, name="knowledge-base"),
    path("moderation", ModeratorView, name="knowledge-base-moderator"),
    path("contribution", ContributorView, name="knowledge-base-contributor"),
]
