from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import InteractiveFictionView, LobbyCreateView, UploadFileView

urlpatterns = [
    # lobbies
    path("lobby/", views.lobby_list, name="lobby-list"),
    path("lobby/create/", LobbyCreateView.as_view(), name="lobby-create"),
    path("lobby/<int:pk>/", views.ViewLobbyDetails.as_view(), name="lobby-details"),
    path("lobby/<int:pk>/join", views.lobby_join, name="lobby-join"),
    path("lobby/<int:pk>/leave", views.lobby_leave, name="lobby-leave"),
    path("lobby/<int:pk>/edit/", views.LobbyUpdateView.as_view(), name="lobby-edit"),
    path("lobby/<int:pk>/delete/", views.LobbyDeleteView.as_view(), name="lobby-delete"),
    # For AJAX req. See lobby_details.html for invocation.
    path("lobby/<int:pk>/update_match_status/", views.update_match_status, name="update_match_status"),
    path("lobby/<int:pk>/flipresult", views.check_guess, name="flip-result"),
    # chat in tournaments
    path("tournaments/<int:pk>/chat/", views.TournamentChatDetailView, name="tournament-chat"),
    # Games favorites
    path("favorites/", views.FavoriteListView.as_view(), name="favorite-list"),
    path("<int:pk>/favorite/", views.add_to_favorites, name="add-to-favorites"),
    path("<int:pk>/unfavorite/", views.remove_from_favorites, name="remove-from-favorites"),
    # custom game list handling
    path("<int:pk>/gamelists/<int:list_pk>/add/", views.add_to_gamelist, name="add-to-gamelist"),
    path("<int:pk>/gamelists/<int:list_pk>/remove/", views.remove_from_gamelist, name="remove-from-gamelist"),
    # games
    path("", views.GameListView.as_view(), name="game-list"),
    path("create/", views.GameCreateView.as_view(), name="game-create"),
    path("<int:pk>/edit", views.GameEditView.as_view(), name="game-edit"),
    path("bgg_search_by_name/", views.bgg_search_by_name, name="bgg_search_by_name"),
    path("search/", views.search_results, name="game-search-results"),
    path("<int:pk>/reviews/", views.ReviewListView.as_view(), name="game-review-list"),
    # interactive fiction
    path("interactive-fiction/", views.InteractiveFictionView.as_view(), name="interactive-fiction"),
    path("<int:pk>/upload/", UploadFileView.as_view(), name="upload-file"),
    path("if-game/<int:pk>/", InteractiveFictionView.as_view(), name="interactive-fiction-detail"),
    # tournaments
    path("tournaments/", views.TournamentListView.as_view(), name="tournament-list"),
    path("tournaments/<int:pk>/", views.TournamentDetailView.as_view(), name="tournament-detail"),
    path("tournaments/create/", views.TournamentCreateView.as_view(), name="tournament-create"),
    path("tournaments/<int:pk>/update/", views.TournamentUpdateView.as_view(), name="tournament-update"),
    path("tournaments/<int:pk>/delete/", views.TournamentDeleteView.as_view(), name="tournament-delete"),
    path("tournaments/archived/", views.TournamentArchivedListView.as_view(), name="tournament-archived"),
    # placeholder game
    path("lobby/<int:pk>/coinflip", views.coin_flip_game, name="placeholder-game"),
    path("<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
    # tournament feedback
    path("tournaments/<int:tournament_id>/feedback/", views.tournament_feedback_list, name="tournament-feedback-list"),
    path("tournaments/<int:tournament_id>/feedback/submit/", views.submit_feedback, name="submit-feedback"),
    path("feedback/update/<int:feedback_id>/", views.update_feedback_view, name="update-feedback"),
    path("feedback/delete/<int:feedback_id>/", views.delete_feedback_view, name="delete-feedback"),
    path("feedback/my-feedback/", views.user_feedback_list, name="user-feedback-list"),
    # Word Game
    path("wordle/", views.wordle_game_page, name="wordle-game"),
    # checkers
    path("checkers/<int:pk>/", views.checkers_game_view, name="checkers-game"),
    path("checkers/<int:board_id>/update/", views.checkers_game_update_board_state, name="update_board_state"),
    path("checkers/<int:board_id>/state/", views.checkers_game_get_board_state, name="checkers-get-state"),
    # tournament feedback
    path("tournaments/<int:tournament_id>/feedback/", views.tournament_feedback_list, name="tournament-feedback-list"),
    path("tournaments/<int:tournament_id>/feedback/submit/", views.submit_feedback, name="submit-feedback"),
]
# for an uploaded twine file this makes the files accessible at a url
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
