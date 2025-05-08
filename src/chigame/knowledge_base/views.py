# Keep model imports for now, as it will be required for WIP features
from django.shortcuts import get_object_or_404, render

from .models import Guide


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


def GuideDetailView(request, pk):
    guide = get_object_or_404(Guide, pk=pk)
    context = {"guide": guide}
    return render(request, "knowledge-base/guide_detail.html", context)


def ModeratorView(request):
    context = {}
    return render(request, "knowledge-base/moderator.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
