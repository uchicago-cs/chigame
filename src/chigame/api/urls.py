from django.urls import path

from . import views

urlpatterns = [
    # GAME API URLS
    path("games/", views.GameListView.as_view(), name="api-game-list"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    # LOBBY API URLS
    path("lobbies/", views.LobbyListView.as_view(), name="api-lobby-list"),
    path("lobbies/<int:pk>/", views.LobbyDetailView.as_view(), name="api-lobby-detail"),
    # USER API URLS
    path("users/", views.UserListView.as_view(), name="api-user-list"),
    path("users/<slug:slug>/", views.UserDetailView.as_view(), name="api-user-detail"),
    path("users/<int:pk>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
    # CHAT API URLS
    path("tournaments/chat/", views.MessageView.as_view(), name="api-chat-list"),
    path("tournaments/chat/feed/", views.MessageFeedView.as_view(), name="api-chat-detail"),
]
