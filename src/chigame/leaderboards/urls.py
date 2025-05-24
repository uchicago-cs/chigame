from django.urls import path

from .views import leaderboard_view, LeaderboardEntryListView

urlpatterns = [
    path("<int:game_id>/", leaderboard_view, name="leaderboard_view"),
    path("api/games/<int:game_id>/leaderboard-entries/", LeaderboardEntryListView.as_view(), name="leaderboard_entry_list"),
]
