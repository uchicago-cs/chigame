from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

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
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="api-user-detail"),
    path("users/<int:pk>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
    # AUTHENTICATION API URLS
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
