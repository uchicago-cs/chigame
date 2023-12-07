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
    path("add/", views.UserRegistrationView.as_view(), name="user-registration"),
    path("<slug:slug>/", views.UserDetailView.as_view(), name="api-user-detail"),
    path("<slug:slug>/groups/", views.UserGroupsView.as_view(), name="api-user-groups"),
    path("<int:pk>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
]

tournament_patterns = [
    path("chat/", views.MessageView.as_view(), name="api-chat-list"),
    path("chat/feed/", views.MessageFeedView.as_view(), name="api-chat-detail"),
]

group_patterns = [
    path("", views.GroupListView.as_view(), name="api-group-list"),
    path("<int:pk>/", views.GroupDetailView.as_view(), name="api-group-detail"),
    path("<int:pk>/members/", views.GroupMembersView.as_view(), name="api-group-members"),
]

urlpatterns = [
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", views.CustomTokenVerifyView.as_view(), name="token_verify"),
    path("games/", include(game_patterns)),
    path("lobbies/", include(lobby_patterns)),
    path("users/", include(user_patterns)),
    path("tournaments/", include(tournament_patterns)),
    path("groups/", include(group_patterns)),
]
