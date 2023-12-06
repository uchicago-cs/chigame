from django.urls import path

from . import views

urlpatterns = [
    path("games/", views.GameListView.as_view(), name="api-game-list"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    path("tournaments/create/", views.TournamentCreateView.as_view(), name="create-tournament"),
    path("tournaments/", views.TournamentListView.as_view(), name="tournament-list"),
    path("register/", views.UserRegistrationView.as_view(), name="user-registration"),
    path("lobbies/", views.LobbyListView.as_view(), name="api-lobby-list"),
    path("lobbies/<int:pk>/", views.LobbyDetailView.as_view(), name="api-lobby-detail"),
    path("users/", views.UserListView.as_view(), name="api-user-list"),
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", views.CustomTokenVerifyView.as_view(), name="token_verify"),
    path("users/<slug:slug>/", views.UserDetailView.as_view(), name="api-user-detail"),
    path("users/<int:pk>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
    path("tournaments/chat/", views.MessageView.as_view(), name="api-chat-list"),
    path("tournaments/chat/feed/", views.MessageFeedView.as_view(), name="api-chat-detail"),
    # GROUP API URLS
    path("groups/<int:pk>/members/", views.GroupMembersView.as_view(), name="api-group-members"),
    path("users/<slug:slug>/groups/", views.UserGroupsView.as_view(), name="api-user-groups"),
]
