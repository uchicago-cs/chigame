from django.urls import path

from chigame.users.views import (
    accept_friend_invitation,
    act_on_inbox_notification,
    bulk_inbox,
    cancel_friend_invitation,
    decline_friend_invitation,
<<<<<<< HEAD
    invite_to_game,
    invite_to_tournament,
=======
    friend_list_view,
>>>>>>> dev
    notification_detail,
    remove_friend,
    send_friend_invitation,
    user_detail_view,
    user_inbox_view,
    user_list,
    user_profile_detail_view,
    user_redirect_view,
    user_search_results,
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
    path("remove_friend/<int:pk>", view=remove_friend, name="remove-friend"),
    path("cancel_friend_invitation/<int:pk>", view=cancel_friend_invitation, name="cancel-friend-invitation"),
    path("invite_to_game/<int:pk>", view=invite_to_game, name="invite-to-game"),
    path("invite_to_tournament/<int:pk>", view=invite_to_tournament, name="invite-to-tournament"),
    path("user-detail/", views.user_detail_view, name="user-detail"),
    path("user-list/", views.user_list, name="user-list"),
    path("accept_friend_invitation/<int:pk>", view=accept_friend_invitation, name="accept-friend-invitation"),
    path("decline_friend_invitation/<int:pk>", view=decline_friend_invitation, name="decline-friend-invitation"),
    path("user_history/<int:pk>", views.user_history, name="user-history"),
    path("search-results", view=user_search_results, name="user-search-results"),
    path("inbox/<int:pk>", view=user_inbox_view, name="user-inbox"),
    path("profile/<int:pk>/friends", view=friend_list_view, name="friend-list"),
    path("inbox/<int:pk>/deleted_notifications", views.deleted_notifications_view, name="deleted-notifications"),
    path("notification_detail/<int:pk>", view=notification_detail, name="notification-detail"),
    path(
        "act_on_inbox_notification/<int:pk>/<str:action>",
        view=act_on_inbox_notification,
        name="act-on-inbox-notification",
    ),
    path("bulk-action/", view=bulk_inbox, name="bulk-inbox"),
]
