from django.urls import path

from chigame.users.views import (
    cancel_friendship,
    send_friend_invitation,
    user_detail_view,
    user_profile_detail_view,
    user_redirect_view,
    user_search_results,
    user_update_view,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("profile/<int:pk>/", view=user_profile_detail_view, name="user-profile"),
    path("add_friend/<int:pk>", view=send_friend_invitation, name="add_friend"),
    path("cancel_friendship/<int:pk>", view=cancel_friendship, name="cancel_friendship"),
    path("search-results/", view=user_search_results, name="search-results"),
]
