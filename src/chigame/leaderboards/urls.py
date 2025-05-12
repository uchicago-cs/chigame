from django.urls import path
from .views import leaderboard_view

urlpatterns = [
    path("leaderboard/<int:game_id>/", leaderboard_view, name="leaderboard_view"),
]
