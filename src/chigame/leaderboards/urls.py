from django.urls import path

from . import views
from .views import leaderboard_view

urlpatterns = [
    path("<int:game_id>/", views.leaderboard_view, name="leaderboard_view"),
    path("bar-chart/<int:game_id>/", views.bar_chart, name="bar_chart"),
    path("bar-chart/time-played/<int:game_id>/", views.top_time_played_bar_chart, name="top_time_played_bar_chart"),
]
