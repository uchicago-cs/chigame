from django.urls import path
from . import views

# Create your urls here

urlpatterns = [
  path("achievements/demo-game", views.demo_game, name="demo-game")
]