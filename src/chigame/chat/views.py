from django.shortcuts import get_object_or_404, render

from .models import LiveChat


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    return render(request, "chat/index.html", {"chat": chat})
