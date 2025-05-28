from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, OuterRef, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import LiveChatForm
from .models import LiveChat, LiveChatMessage, LiveChatMessageReaction, LiveChatUser
from .utils import get_profanity_list_json


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    messages = LiveChatMessage.objects.filter(live_chat=chat).order_by("sent_at")
    chat_user = LiveChatUser.objects.filter(live_chat=chat, user=request.user).first()
    profanity_enabled = not chat.profanity_allowed or (chat_user and chat_user.profanity)
    profanity_words = get_profanity_list_json()
    # if the chat is public, add the request user to the chat
    if request.user.is_authenticated and chat.public and not chat.users.filter(id=request.user.id).exists():
        chat.users.add(request.user)

    # Handle background image upload
    if request.method == "POST" and "background" in request.FILES:
        if request.user in chat.users.all():
            chat.background_image = request.FILES["background"]
            chat.save()
    return render(request, "chat/index.html", {"chat": chat, "messages": messages})

@login_required
def toggle_profanity(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # Find the LiveChatUser object for the current user across any chat
        # (You may want to scope this per chat ID if needed)
        chat_users = LiveChatUser.objects.filter(user=request.user)
        if not chat_users.exists():
            return JsonResponse({"error": "No chat user records found"}, status=404)

        new_value = not chat_users.first().profanity

        for cu in chat_users:
            cu.profanity = new_value
            cu.save()

        return JsonResponse({"success": True, "profanity_enabled": new_value})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
