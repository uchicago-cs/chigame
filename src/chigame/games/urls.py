from django.urls import path

from . import views
from .views import LobbyListView, TournamentCreateView

urlpatterns = [
    path("lobby/", LobbyListView.as_view(), name="lobby-list"),
    path("lobby/<int:pk>/", views.ViewLobbyDetails.as_view(), name="lobby-details"),
    path("", views.GameListView.as_view(), name="game-list"),
    path("create/", views.GameCreateView.as_view(), name="game-create"),
    path("<int:pk>/edit", views.GameEditView.as_view(), name="game-edit"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
    # tournaments
    path("tournaments/", views.TournamentListView.as_view(), name="tournament-list"),
    path("tournaments/create/", TournamentCreateView.as_view(), name="tournament-create"),
]
