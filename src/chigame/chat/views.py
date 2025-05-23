from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import LiveChat, LiveChatMessage, LiveChatMessageReaction, LiveChatUser


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    messages = LiveChatMessage.objects.filter(live_chat=chat).order_by("sent_at")

    # if the chat is public, add the request user to the chat
    if request.user.is_authenticated and chat.public and not chat.users.filter(id=request.user.id).exists():
        chat.users.add(request.user)

    return render(request, "chat/index.html", {"chat": chat, "messages": messages})


def live_chat_list(request):
    chats = LiveChat.objects.filter(public=True)
    return render(request, "chat/live-chat-list.html", {"chats": chats})


def delete_message(request, message_id):
    """
    Deletes a message from the database.

    Args:
        request: The request object.
        message_id: The id of the message to delete.

    Returns:
        A JSON response.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    message = get_object_or_404(LiveChatMessage, id=message_id)

    if not request.user == message.user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    message.delete()

    return JsonResponse({"message": "Message deleted successfully"}, status=200)


def pin_message(request, message_id):
    """
    Pins a message in the chat

    Args:
        request: The request object.
        message_id: The id of the message to delete.

    Returns:
        A JSON response.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    message = get_object_or_404(LiveChatMessage, id=message_id)

    if not message.live_chat.users.filter(id=request.user.id).exists():
        return JsonResponse({"error": "Unauthorized"}, status=401)

    chat = message.live_chat
    chat.pinned_message = message
    chat.save()

    return JsonResponse(
        {
            "message": "Message pinned successfully",
            "pinned_message": {
                "id": message.id,
                "content": message.content,
                "username": message.user.username or message.user.email,
                "is_pinned": True,
            },
        },
        status=200,
    )


@csrf_exempt
@require_POST
def react_to_message(request, message_id):
    """
    Reacts to a message in the database, creating a new reaction.

    Args:
        request: The request object.
        message_id: The id of the message to react to.
        content: Content of message reaction (validated as single emoji).

    Returns:
        A JSON response.
    """
    content = request.POST.get("content")
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    message = get_object_or_404(LiveChatMessage, id=message_id)
    try:
        existing = LiveChatMessageReaction.objects.filter(user=request.user, message=message, content=content)
        if existing.exists():
            existing.delete()  # deletes the reaction if one exists
            return JsonResponse({"status": "unreacted", "content": content}, status=200)
        else:
            LiveChatMessageReaction.objects.create(
                user=request.user, message=message, content=content
            )  # otherwise, creates a new one
            return JsonResponse({"status": "reacted", "content": content}, status=200)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)  # not a single emoji


def edit_message(request, message_id):
    """
    Edits a message from the database.

    Args:
        request: The request object.
        message_id: The id of the message to edit.

    Returns:
        A JSON response.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    message = get_object_or_404(LiveChatMessage, id=message_id)

    if not request.user == message.user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method == "POST":
        content = request.POST.get("content")
        message.edited = True
        message.content = content
        message.save()
        return JsonResponse({"message": "Message edited successfully", "edited": message.edited}, status=200)

    return JsonResponse({"message": "Type of request not allowed"}, status=405)


@login_required
def toggle_profanity(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # Find the LiveChatUser object for the current user across any chat
        # (You may want to scope this per chat ID if needed)
        chat_user = LiveChatUser.objects.filter(user=request.user).first()
        if not chat_user:
            return JsonResponse({"error": "LiveChatUser not found"}, status=404)

        chat_user.profanity = not chat_user.profanity
        chat_user.save()

        return JsonResponse({"success": True, "profanity_enabled": chat_user.profanity})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
