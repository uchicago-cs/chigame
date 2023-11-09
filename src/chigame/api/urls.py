from django.urls import path

from . import views

urlpatterns = [
    path("games/", views.GameListView.as_view(), name="api-game-list"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="api-game-detail"),
    path("users/", views.UserListView.as_view(), name="api-user-list"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="api-user-detail"),
]
