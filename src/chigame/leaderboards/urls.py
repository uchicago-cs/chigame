from django.urls import path

from .views import leaderboard_view
from . import views

urlpatterns = [
    path("<int:game_id>/", views.leaderboard_view, name="leaderboard_view"),
    path("bar-chart/<int:game_id>/", views.bar_chart, name="bar_chart")
]
