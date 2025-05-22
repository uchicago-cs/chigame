from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

game_patterns = [
    path("", views.GameListView.as_view(), name="api-game-list"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    path("<int:pk>/categories/", views.GameCategoriesAPIView.as_view(), name="api-game-asdcategories"),
    path("<int:pk>/mechanics/", views.GameMechanicsAPIView.as_view(), name="api-game-mechanics"),
    path("<int:pk>/reviews/", views.GameReviewListView.as_view(), name="api-game-reviews"),
    path("<int:pk>/reviews/create/", views.ReviewCreateView.as_view(), name="api-game-review-create"),
    path("<int:game_id>/reviews/<int:pk>/", views.ReviewDetailView.as_view(), name="api-game-review-detail"),
    path("<int:pk>/achievements/", views.AchievementListView.as_view(), name="api-game-achievements"),
    path(
        "<int:game_id>/achievements/<int:pk>/assign/",
        views.UserAchievementCreateView.as_view(),
        name="api-user-achievement-assignment",
    ),
    path("<int:pk>/achievements/create/", views.AchievementCreateView.as_view(), name="api-game-achievement-create"),
    path("<int:game_id>/scores/", views.MetricScoreView.as_view(), name="api-game-submit-score"),
    path("<int:pk>/popups/", views.GamePopupsAPIView.as_view(), name="api-game-popups"),
    path("data/", views.GameDataListView.as_view(), name="api-game-data-list"),
    path("<int:game_id>/data/<str:key>/", views.GameDataDetailView.as_view(), name="api-game-data-detail"),
    path("<int:pk>/review-stats/", views.GameReviewStatsAPIView.as_view(), name="api-game-review-stats"),
]

lobby_patterns = [
    path("", views.LobbyListView.as_view(), name="api-lobby-list"),
    path("<int:pk>/", views.LobbyDetailView.as_view(), name="api-lobby-detail"),
]

user_patterns = [
    path("", views.UserListView.as_view(), name="api-user-list"),
    path("<slug:slug>/", views.UserDetailView.as_view(), name="api-user-detail"),
    path("<slug:slug>/groups/", views.UserGroupsView.as_view(), name="api-user-groups"),
    path("<int:pk>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
    path(
        "<int:user_id>/achievements/<int:pk>",
        views.UserAchievementDetailView.as_view(),
        name="api-user-achievements-edit",
    ),
    path("<int:pk>/achievements/", views.UserAchievementListView.as_view(), name="api-user-achievements"),
]

tournament_patterns = [
    path("chat/", views.MessageView.as_view(), name="api-chat-list"),
    path("chat/feed/", views.MessageFeedView.as_view(), name="api-chat-detail"),
    path("<int:pk>/simulate/", views.TournamentSimulationView.as_view(), name="api-tournament-simulate"),
    path("<int:pk>/feedback/", views.FeedbackListCreateView.as_view(), name="api-feedback-list-create"),
    path("feedback/<int:pk>/", views.FeedbackDetailView.as_view(), name="api-feedback-detail"),
]

group_patterns = [
    path("", views.GroupListView.as_view(), name="api-group-list"),
    path("<int:pk>/", views.GroupDetailView.as_view(), name="api-group-detail"),
    path("<int:pk>/members/", views.GroupMembersView.as_view(), name="api-group-members"),
    path("<int:pk>/join/", views.GroupJoinView.as_view(), name="api-group-join"),
    path("<int:pk>/leave/", views.GroupLeaveView.as_view(), name="api-group-leave"),
]

login_patterns = [
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]


livechat_patterns = [
    path("create/", views.LiveChatCreateView.as_view(), name="api-livechat-create"),
    path("list/", views.LiveChatListView.as_view(), name="api-livechat-list"),
    path("<int:chat_id>/add_user/", views.LiveChatAddUserView.as_view(), name="api-livechat-add-user"),
    path("<int:pk>/", views.LiveChatDetailView.as_view(), name="api-livechat-detail"),
]

urlpatterns = [
    path("games/", include(game_patterns)),
    path("lobbies/", include(lobby_patterns)),
    path("users/", include(user_patterns)),
    path("tournaments/", include(tournament_patterns)),
    path("groups/", include(group_patterns)),
    path("login/", include(login_patterns)),
    path("livechats/", include(livechat_patterns)),
]
