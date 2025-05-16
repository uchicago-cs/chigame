from django.urls import path

from . import views

urlpatterns = [path("demo-game", views.demo_game, name="demo-game")]
