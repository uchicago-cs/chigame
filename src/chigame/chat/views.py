from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import LiveChatForm
from .models import LiveChat, LiveChatMessage, LiveChatMessageReaction


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


def leave_chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)

    if request.user in chat.users.all():
        chat.users.remove(request.user)

        if chat.users.count() == 0:
            chat.delete()
    return redirect("live-chat-list")


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


def live_chat_preview_api(request):
    chats = LiveChat.objects.all()  # or filter(is_public=True) if appropriate
    return JsonResponse(
        {
            "chats": [
                {"id": chat.id, "name": chat.name, "description": getattr(chat, "description", "")} for chat in chats
            ]
        }
    )
