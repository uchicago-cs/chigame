from django.urls import path

from . import views

urlpatterns = [
    path("", views.GameListView.as_view(), name="games-list"),
    path("lobby/<int:pk>/match/create/", views.match_init, name="match-init"),
]
