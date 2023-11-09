from django.urls import path

from . import views

urlpatterns = [
    path("games/", views.GameListView.as_view(), name="api-game-list"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    # USER API URLS
    path("users/<int:pk>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
]
