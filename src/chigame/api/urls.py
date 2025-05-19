from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

game_patterns = [
    path("", views.GameListView.as_view(), name="api-game-list"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    path("<int:pk>/categories/", views.GameCategoriesAPIView.as_view(), name="api-game-categories"),
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
]

tournament_patterns = [
    path("chat/", views.MessageView.as_view(), name="api-chat-list"),
    path("chat/feed/", views.MessageFeedView.as_view(), name="api-chat-detail"),
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

urlpatterns = [
    path("games/", include(game_patterns)),
    path("lobbies/", include(lobby_patterns)),
    path("users/", include(user_patterns)),
    path("tournaments/", include(tournament_patterns)),
    path("groups/", include(group_patterns)),
    path("login/", include(login_patterns)),
]
