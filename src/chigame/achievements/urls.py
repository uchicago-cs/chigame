from django.urls import path

from . import views

urlpatterns = [
    path("demo-game", views.demo_game, name="demo-game"),
    path("", views.user_achievements, name="user_achievements"),
    path("<int:pk>/", views.user_achievements, name="user_achievements"),
]
