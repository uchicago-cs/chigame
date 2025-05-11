from django.urls import path
from .views import ContributorMdUpload, ContributorView, DefaultView, ModeratorGuidesPending

urlpatterns = [
    path("", DefaultView.as_view(), name="knowledge-base"),
    path("moderation", ModeratorGuidesPending.as_view(), name="knowledge-base-moderator"),
    path("contribution", ContributorView, name="knowledge-base-contributor"),
    path("upload", ContributorMdUpload, name="knowledge-base-guide-upload"),
    path("<int:pk>/reupload", ContributorMdUpload, name="knowledge-base-guide-reupload"),
]

# Eventually, we should add '!<slug:username>' the contribution path so we can
# list all the guides associated with the current user
