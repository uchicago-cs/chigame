from django.shortcuts import get_object_or_404, render

from .models import LiveChat, LiveChatMessage


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    messages = LiveChatMessage.objects.filter(live_chat=chat).order_by("sent_at")

    # Handle background image upload
    if request.method == "POST" and "background" in request.FILES:
        if request.user in chat.users.all():
            chat.background_image = request.FILES["background"]
            chat.save()
    return render(request, "chat/index.html", {"chat": chat, "messages": messages})
