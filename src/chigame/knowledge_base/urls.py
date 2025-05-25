"""
URL patterns for the knowledge base app.
These URLs handle guide viewing, moderation, and user feedback functionality.
"""

from django.urls import path

from .views import (
    ContributorManageGuide,
    ContributorMdUpload,
    DefaultView,
    DownloadGuide,
    FeedbackDetail,
    GuideDetail,
    ModeratorGuidesPending,
    ModeratorListByGame,
    ModeratorSetPublishedGuide,
    ModeratorSingleGame,
    ReviewPendingGuideView,
    UserFeedbackView,
    faq_view,
)

urlpatterns = [
    path("", DefaultView.as_view(), name="knowledge-base"),
    path("guides/<int:pk>", GuideDetail.as_view(), name="knowledge-base-guide-detail"),
    path("moderation", ModeratorGuidesPending.as_view(), name="knowledge-base-moderator"),
    path("moderation/review/<int:pk>", ReviewPendingGuideView.as_view(), name="moderator-review-guide"),
    path("manage-my-guides", ContributorManageGuide.as_view(), name="contributor-manage-guide"),
    path("guides/<int:pk>/download", DownloadGuide, name="download-guide"),
    path("manage-my-guides/feedback/<int:pk>", FeedbackDetail.as_view(), name="feedback-detail"),
    path("upload", ContributorMdUpload, name="knowledge-base-guide-upload"),
    path("guides/<int:pk>/reupload", ContributorMdUpload, name="knowledge-base-guide-reupload"),
    path("feedback", UserFeedbackView.as_view(), name="knowledge-base-feedback"),
    path("faq", faq_view, name="knowledge-base-faq"),
    path("moderation/review/games", ModeratorListByGame.as_view(), name="moderator-manage-by-game"),
    path("moderation/review/games/<int:game_pk>", ModeratorSingleGame.as_view(), name="moderator-single-game"),
    path(
        "moderation/review/games/<int:game_pk>/set-published/<int:guide_pk>",
        ModeratorSetPublishedGuide,
        name="moderator-set-publish-guide",
    ),
]
