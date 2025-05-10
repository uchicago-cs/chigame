from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from .models import LiveChat, LiveChatMessage


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    messages = LiveChatMessage.objects.filter(live_chat=chat)
    
    return render(request, "chat/index.html", {"chat": chat, "messages": messages})
