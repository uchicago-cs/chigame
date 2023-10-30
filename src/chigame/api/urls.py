from django.urls import path

from . import views

urlpatterns = [
    path("games/", views.GameListView.as_view()),
    path("games/<int:pk>/", views.GameDetailView.as_view()),
]
