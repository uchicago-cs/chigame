from django.urls import path

from . import views

app_name = "forums"
urlpatterns = [
    path("create", view=views.ForumCreateView.as_view(), name="forum-create"),
]
