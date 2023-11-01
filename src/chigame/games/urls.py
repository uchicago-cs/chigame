from django.urls import path

from . import views

urlpatterns = [
    path("", views.GameListView.as_view(), name="games-list"),
    path("lobby/", views.lobby_list, name="lobby-list"),
    path('lobby/<int:lobby_id>/', views.lobby_detail, name='lobby_detail'),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
]
