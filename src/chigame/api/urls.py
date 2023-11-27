from django.urls import include, path

from . import views

game_patterns = [
    path("", views.GameListView.as_view(), name="api-game-list"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    path("<int:pk>/categories/", views.GameCategoriesAPIView.as_view(), name="api-game-categories"),
    path("<int:pk>/mechanics/", views.GameMechanicsAPIView.as_view(), name="api-game-mechanics"),
]

lobby_patterns = [
    path("", views.LobbyListView.as_view(), name="api-lobby-list"),
    path("<int:pk>/", views.LobbyDetailView.as_view(), name="api-lobby-detail"),
]

user_patterns = [
    path("", views.UserListView.as_view(), name="api-user-list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="api-user-detail"),
    path("<int:pk>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
]

urlpatterns = [
    # GAME API URLS
    path("games/", include(game_patterns)),
    # LOBBY API URLS
    path("lobbies/", include(lobby_patterns)),
    # USER API URLS
    path("users/", include(user_patterns)),
]
