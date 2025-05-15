from django.urls import path

from .views import landing_page_view, leaderboard_view

urlpatterns = [
    path("", landing_page_view, name="leaderboards_landing"),
    path("<int:game_id>/", leaderboard_view, name="leaderboard_view"),
]
