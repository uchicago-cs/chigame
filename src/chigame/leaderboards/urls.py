from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing_page_view, name="leaderboards_landing"),
    path("<int:game_id>/", views.leaderboard_view, name="leaderboard_view"),
    path("bar-chart/<int:game_id>/", views.bar_chart, name="bar_chart"),
]
