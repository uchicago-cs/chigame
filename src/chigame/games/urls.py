from django.urls import path

from . import views

urlpatterns = [
    path("lobby/", views.lobby_list, name="lobby-list"),
    path("lobby/<int:pk>/", views.ViewLobbyDetails.as_view(), name="lobby-details"),
    path("", views.GameListView.as_view(), name="game-list"),
    path("create/", views.GameCreateView.as_view(), name="game-create"),
    path("<int:pk>/edit", views.GameEditView.as_view(), name="game-edit"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
    # tournaments
    path("tournaments/", views.TournamentsListView.as_view(), name="tournament-list"),
    path("tournaments/<int:pk>/", views.TournamentDetailView.as_view(), name="tournament-detail"),
    path("tournaments/create/", views.TournamentCreateView.as_view(), name="tournament-create"),
    path("tournaments/<int:pk>/update/", views.TournamentUpdateView.as_view(), name="tournament-update"),
    path("tournaments/<int:pk>/delete/", views.TournamentDeleteView.as_view(), name="tournament-delete"),
]