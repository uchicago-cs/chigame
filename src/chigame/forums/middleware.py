"""
Prevent unauthenticated users from manipulating the forum or requesting any
pages beyond the index, landing page
"""

from django.shortcuts import redirect


class ForumAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "/forums/" in request.path and not request.path.endswith("/forums/") and not request.user.is_authenticated:
            return redirect("/forums")  # Adjust the URL name as needed
        return self.get_response(request)
