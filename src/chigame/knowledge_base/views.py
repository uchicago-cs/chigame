# Keep model imports for now, as it will be required for WIP features
# from .models import *
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from .models import Guide


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


def ModeratorGuidesPending(request):
    pending_guides = Guide.objects.filter(status=0)
    context = {"pendingGuides": pending_guides}
    return render(request, "knowledge-base/moderator_pending_guides.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
