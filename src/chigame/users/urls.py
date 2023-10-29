from django.urls import path

from chigame.users.views import send_friend_invitation, user_detail_view, user_redirect_view, user_update_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("add_friend/<int:pk>", view=send_friend_invitation, name="add_friend"),
]
