from django.urls import path
from . import views

urlpatterns = [path("achievements/demo-game", views.demo_game, name="demo-game")]
