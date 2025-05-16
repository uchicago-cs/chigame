from django.shortcuts import get_object_or_404, redirect, render

from .forms import LiveChatForm
from .models import LiveChat, LiveChatMessage


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    messages = LiveChatMessage.objects.filter(live_chat=chat).order_by("sent_at")

    # if the chat is public, add the request user to the chat
    if chat.public and not chat.users.filter(id=request.user.id).exists():
        chat.users.add(request.user)
    if request.user.is_authenticated and not chat.users.filter(id=request.user.id).exists():
        chat.users.add(request.user)
    return render(request, "chat/index.html", {"chat": chat, "messages": messages})


def live_chat_list(request):
    chats = LiveChat.objects.all()
    return render(request, "chat/live-chat-list.html", {"chats": chats})


def create_live_chat(request):
    if request.method == "POST":
        form = LiveChatForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("live-chat-list")
    else:
        form = LiveChatForm()
    return render(request, "chat/create-live-chat.html", {"form": form})
