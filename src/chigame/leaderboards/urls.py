from django.urls import path

from .views import leaderboard_view, privacy_setting_delete, privacy_setting_list, privacy_setting_manage

urlpatterns = [
    path("<int:game_id>/", leaderboard_view, name="leaderboard_view"),
    # ======== Privacy Settings ========
    # list all privacy settings for the current user
    path("privacy/", privacy_setting_list, name="privacy-list"),
    # Global privacy setting create/update
    path("privacy/manage/", privacy_setting_manage, name="privacy-manage-global"),
    # Game-level create/update
    path("privacy/manage/game/<int:game_id>/", privacy_setting_manage, name="privacy-manage-game"),
    # Specific leaderboard create/update
    path(
        "privacy/manage/game/<int:game_id>/leaderboard/<int:leaderboard_id>/",
        privacy_setting_manage,
        name="privacy-manage-leaderboard",
    ),
    # Delete leaderboard privacy setting
    path("privacy/<int:pk>/delete/", privacy_setting_delete, name="privacy-delete")
    # ==================================
]
