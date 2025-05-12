from django.urls import path

from .views import leaderboard_view

urlpatterns = [path("<int:game_id>/", leaderboard_view, name="leaderboard_view")]
