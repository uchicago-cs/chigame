from django.urls import path

from . import views

urlpatterns = [
    path("", views.GameListView.as_view(), name="games-list"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
]
