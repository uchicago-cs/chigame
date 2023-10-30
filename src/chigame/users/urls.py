from django.urls import path

from chigame.users.views import user_detail_view, user_redirect_view, user_update_view, user_list

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path('user-list/', view=user_list, name='user_list'),
]
