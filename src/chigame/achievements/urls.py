from django.urls import path

from . import views

urlpatterns = [
    path("demo-game", views.demo_game, name="demo-game"),
    path("toggle-pin/<int:achievement_id>/", views.toggle_pin_achievement, name="toggle_pin_achievement"),
    path("", views.user_achievements, name="user_achievements"),
    path("<int:user_id>/", views.user_achievements, name="user_achievements"),
]
