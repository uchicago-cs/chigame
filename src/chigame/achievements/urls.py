from django.urls import path
from django.conf.urls import include

from . import views

urlpatterns = [path("demo-game", views.demo_game, name="demo-game")]
