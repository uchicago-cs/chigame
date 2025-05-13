from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import LiveChat, LiveChatMessage


def chat(request, chat_id):
    chat = get_object_or_404(LiveChat, id=chat_id)
    messages = LiveChatMessage.objects.filter(live_chat=chat).order_by("sent_at")

    return render(request, "chat/index.html", {"chat": chat, "messages": messages})


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
        message.content = content
        message.save()
        return JsonResponse({"message": "Message edited successfully"}, status=200)
    
    return JsonResponse({"message": "Type of request not allowed"}, status=405)
