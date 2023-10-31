from django.urls import path

from . import views

urlpatterns = [
    path("", views.GameListView.as_view(), name="games-list"),
    path("lobby/", views.lobby_list, name="lobby-list"),
    path("lobby/<int:pk>/", views.ViewLobbyDetails.as_view(), name ="lobby-details"),
]
