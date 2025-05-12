from django.shortcuts import redirect, render


def chatPage(request):
    """
    This is the main page for the chat. This is what you would edit if you would like to add a login system, etc.

    Returns:
        HttpResponse: The response object.
    """
    if not request.user.is_authenticated:
        return redirect("login-user")

    # if you wanted to implement chats loaded from db (stored) you would implement some sort of arg here
    # you would also add, like in the chat app, messages fetched from that chat

    return render(request, "chat/chatPage.html", {})
