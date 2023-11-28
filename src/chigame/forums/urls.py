from django.urls import path

from . import views

app_name = "forums"
urlpatterns = [path("create", view=views.forum_create, name="forum-create")]
