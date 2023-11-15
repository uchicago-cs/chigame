from django.urls import path

from chigame.users.views import (
    accept_friend_invitation,
    cancel_friend_invitation,
    decline_friend_invitation,
    send_friend_invitation,
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
    path("user-detail/", views.user_detail, name="user-detail"),  # Modified this
    path("user-list/", views.user_list, name="user-list"),
    path("accept_friend_invitation/<int:pk>", view=accept_friend_invitation, name="accept-friend-invitation"),
    path("decline_friend_invitation/<int:pk>", view=decline_friend_invitation, name="decline-friend-invitation"),
    path("user_history/<int:pk>", views.user_history, name="user-history"),
]
