from django.urls import path

from . import views

urlpatterns = [
    path("games/", views.GameListView.as_view(), name="api-game-list"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    path("api/tournaments/create/", views.TournamentCreateView.as_view(), name="create-tournament"),
    path("api/tournaments/", views.TournamentListView.as_view(), name="tournament-list"),
    path("api/register/", views.UserRegistrationView.as_view(), name="user-registration"),
]
