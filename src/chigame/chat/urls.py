from django.urls import path, include

urlpatterns = [
    path("", views.chat, name="chat-page"),
]
