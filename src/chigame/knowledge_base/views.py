# Keep model imports for now, as it will be required for WIP features
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from .models import Guide


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


def GuideDetailView(request, pk):
    guide = get_object_or_404(Guide, pk=pk)
    context = {"guide": guide}
    return render(request, "knowledge-base/guide_detail.html", context)


@login_required
def ModeratorGuidesPending(request):
    if not request.user.moderator:
        raise PermissionDenied()
    pending_guides = Guide.objects.filter(status=0)
    context = {"pendingGuides": pending_guides}
    return render(request, "knowledge-base/moderator_pending_guides.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
