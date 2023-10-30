from django.urls import path
from . import views

urlpatterns = [
    path('bgg-search/', views.bgg_search_view, name='bgg_search_view'),
    path("", views.GameListView.as_view(), name="games-list"),
]


