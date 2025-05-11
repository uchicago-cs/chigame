from django.urls import path

from .views import ContributorManageGuide, DefaultView, DownloadGuide, FeedbackDetail, ModeratorView

urlpatterns = [
    path("", DefaultView.as_view(), name="knowledge-base"),
    path("moderation", ModeratorView, name="knowledge-base-moderator"),
    path("manage-my-guides", ContributorManageGuide.as_view(), name="contributor-manage-guide"),
    path("guides/<int:pk>/download/", DownloadGuide, name="download-guide"),
    path("manage-my-guides/feedback/<int:pk>", FeedbackDetail.as_view(), name="feedback-detail"),
]

# Eventually, we should add '!<slug:username>' the contribution path so we can
# list all the guides associated with the current user
