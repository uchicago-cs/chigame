from django.urls import path

from .views import (
    ContributorManageGuide,
    ContributorMdUpload,
    DefaultView,
    DownloadGuide,
    FeedbackDetail,
    ModeratorGuidesPending,
    ReviewPendingGuideView,
)

urlpatterns = [
    path("", DefaultView.as_view(), name="knowledge-base"),
    path("moderation", ModeratorGuidesPending.as_view(), name="knowledge-base-moderator"),
    path("moderation/review/<int:pk>", ReviewPendingGuideView.as_view(), name="moderator-review-guide"),
    path("manage-my-guides", ContributorManageGuide.as_view(), name="contributor-manage-guide"),
    path("guides/<int:pk>/download", DownloadGuide, name="download-guide"),
    path("manage-my-guides/feedback/<int:pk>", FeedbackDetail.as_view(), name="feedback-detail"),
    path("upload", ContributorMdUpload, name="knowledge-base-guide-upload"),
    path("guides/<int:pk>/reupload", ContributorMdUpload, name="knowledge-base-guide-reupload"),
]

# Eventually, we should add '!<slug:username>' the contribution path so we can
# list all the guides associated with the current user
