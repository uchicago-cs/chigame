from django.urls import path

from .views import ContributorManageGuide, DefaultView, DownloadGuide, ModeratorView

urlpatterns = [
    path("", DefaultView, name="knowledge-base"),
    path("moderation", ModeratorView, name="knowledge-base-moderator"),
    path("manage-my-guides", ContributorManageGuide, name="knowledge-base-contributor"),
    path("guides/<int:pk>/download-md/", DownloadGuide, name="download-guide"),
]

# Eventually, we should add '!<slug:username>' the contribution path so we can
# list all the guides associated with the current user
