from django.urls import path

from . import views

urlpatterns = [
    path("", views.markdown_content_view, name="markdown_content"),
    path("minimal/", views.markdown_content_view, {"minimal": True}, name="minimal_content"),
]
