from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404, render

from .models import LiveChat, LiveChatMessage


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    messages = LiveChatMessage.objects.filter(live_chat=chat).order_by("sent_at")

    # if the chat is public, add the request user to the chat
    if request.user.is_authenticated and chat.public and not chat.users.filter(id=request.user.id).exists():
        chat.users.add(request.user)

    return render(request, "chat/index.html", {"chat": chat, "messages": messages})


def live_chat_list(request):
    latest_message = LiveChatMessage.objects.filter(live_chat=OuterRef("pk")).order_by("-sent_at")

    public_chats = LiveChat.objects.filter(public=True).annotate(
        user_count=Count("users"),
        last_message=Subquery(latest_message.values("content")[:1]),
        last_message_time=Subquery(latest_message.values("sent_at")[:1]),
    )

    private_chats = LiveChat.objects.filter(public=False, users=request.user).annotate(
        user_count=Count("users"),
        last_message=Subquery(latest_message.values("content")[:1]),
        last_message_time=Subquery(latest_message.values("sent_at")[:1]),
    )
    return render(
        request,
        "chat/live-chat-list.html",
        {
            "public_chats": public_chats,
            "private_chats": private_chats,
        },
    )
