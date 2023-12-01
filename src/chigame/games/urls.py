from django.urls import path

from . import views
from .views import LobbyCreateView

urlpatterns = [
    # lobbies
    path("lobby/", views.lobby_list, name="lobby-list"),
    path("lobby/create/", LobbyCreateView.as_view(), name="lobby-create"),
    path("lobby/<int:pk>/", views.ViewLobbyDetails.as_view(), name="lobby-details"),
    path("lobby/<int:pk>/join", views.lobby_join, name="lobby-join"),
    path("lobby/<int:pk>/leave", views.lobby_leave, name="lobby-leave"),
    path("lobby/<int:pk>/edit/", views.LobbyUpdateView.as_view(), name="lobby-edit"),
    path("lobby/<int:pk>/delete/", views.LobbyDeleteView.as_view(), name="lobby-delete"),
    # games
    path("", views.GameListView.as_view(), name="game-list"),
    path("create/", views.GameCreateView.as_view(), name="game-create"),
    path("<int:pk>/edit", views.GameEditView.as_view(), name="game-edit"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
    path("search/", views.search_results, name="game-search-results"),
    # tournaments
    path("tournaments/", views.TournamentListView.as_view(), name="tournament-list"),
    path("tournaments/<int:pk>/", views.TournamentDetailView.as_view(), name="tournament-detail"),
    path("tournaments/create/", views.TournamentCreateView.as_view(), name="tournament-create"),
    path("tournaments/<int:pk>/update/", views.TournamentUpdateView.as_view(), name="tournament-update"),
    path("tournaments/<int:pk>/delete/", views.TournamentDeleteView.as_view(), name="tournament-delete"),
    # placeholder game
    path("lobby/<int:pk>/coinflip", views.coin_flip_game, name="placeholder-game"),
    path("lobby/<int:pk>/flipresult", views.check_guess, name="flip-result"),
    # chat in tournaments
    path("tournaments/<int:pk>/chat/", views.TournamentChatDetailView, name="tournament-chat"),
]
