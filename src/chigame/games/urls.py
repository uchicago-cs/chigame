from django.urls import path

from . import views

urlpatterns = [
    path("", views.GameListView.as_view(), name="game-list"),
    path("create/", views.GameCreateView.as_view(), name="game-create"),
    path("<int:pk>/edit", views.GameEditView.as_view(), name="game-edit"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
]
