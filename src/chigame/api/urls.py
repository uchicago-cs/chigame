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
    path(
        "friend-invitations/send/<int:sender_pk>/<int:receiver_pk>/",
        views.SendFriendInvitationView.as_view(),
        name="send-friend-invitation",
    ),
    path(
        "friend-invitations/accept/<int:invitation_pk>/",
        views.AcceptFriendInvitationView.as_view(),
        name="accept-friend-invitation",
    ),
    path("friend-invitations/", views.FriendInvitationList.as_view(), name="friend-invitation-list"),
    path("user-profiles/create/<int:user_pk>/", views.UserProfileCreateView.as_view(), name="create-user-profile"),
    path("user-profiles/", views.UserProfileListView.as_view(), name="user-profile-list"),
    path(
        "user-profiles/update/<int:user_profile_pk>/",
        views.UserProfileUpdateView.as_view(),
        name="update-user-profile",
    ),
    path("tournaments/chat/feed/", views.MessageFeedView.as_view(), name="api-chat-detail"),
]
