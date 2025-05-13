from django.conf import settings

from .models import Notification


def allauth_settings(request):
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }


def user_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(receiver=request.user, visible=True).order_by("-last_sent")
        return {"header_notifications": notifications}
    return {}
