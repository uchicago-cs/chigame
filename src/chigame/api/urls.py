from django.urls import path

from . import views

urlpatterns = [
    path("games/", views.GameListView.as_view(), name="api-game-list"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    # USER API URLS
    path("users/", views.UserProfileListView.as_view(), name="api-user-list"),
    path("users/<int:pk>/", views.UserProfileDetailView.as_view(), name="api-user-detail"),
    path("users/<int:user_id>/friends/", views.UserFriendsAPIView.as_view(), name="api-user-friends"),
]
