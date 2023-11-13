from django.urls import path

from chigame.users.views import (
    cancel_friend_invitation,
    send_friend_invitation,
    remove_friend,
    invite_to_game,
    invite_to_tournament,
    user_detail_view,
    user_profile_detail_view,
    user_redirect_view,
    user_update_view,
)

from . import views

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("profile/<int:pk>/", view=user_profile_detail_view, name="user-profile"),
    path("add_friend/<int:pk>", view=send_friend_invitation, name="add-friend"),
    path("cancel_friend_invitation/<int:pk>", view=cancel_friend_invitation, name="cancel-friend-invitation"),
    path("remove_friend/<int:pk>", view=remove_friend, name="remove-friend"),
    path("invite_to_game/<int:pk>", view=invite_to_game, name="invite-to-game"),
    path("invite_to_tournament/<int:pk>", view=invite_to_tournament, name="invite-to-tournament"),
    path("user-list/", views.user_list, name="user_list"),
]
