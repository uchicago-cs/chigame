from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing_page_view, name="leaderboards_landing"),
    path("<int:game_id>/", views.leaderboard_view, name="leaderboard_view"),
    path("bar-chart/points/<int:game_id>/", views.points_bar_chart, name="points_bar_chart"),
    path("bar-chart/time-played/<int:game_id>/", views.top_time_played_bar_chart, name="top_time_played_bar_chart"),
    path("bar-chart/games-won/<int:game_id>/", views.top_games_won_bar_chart, name="top_games_won_bar_chart"),
    # ======== Privacy Settings ========
    # list all privacy settings for the current user
    path("privacy/", views.privacy_setting_list, name="privacy-list"),
    # Global privacy setting create/update
    path("privacy/manage/", views.privacy_setting_manage, name="privacy-manage-global"),
    # Game-level create/update
    path("privacy/manage/game/<int:game_id>/", views.privacy_setting_manage, name="privacy-manage-game"),
    # Specific leaderboard create/update
    path(
        "privacy/manage/game/<int:game_id>/leaderboard/<int:leaderboard_id>/",
        views.privacy_setting_manage,
        name="privacy-manage-leaderboard",
    ),
    # Delete leaderboard privacy setting
    path("privacy/<int:pk>/delete/", views.privacy_setting_delete, name="privacy-delete")
    # ==================================
]
