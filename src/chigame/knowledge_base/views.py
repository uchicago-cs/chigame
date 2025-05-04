# Keep model imports for now, as it will be required for WIP features
from django.shortcuts import get_object_or_404, render

from chigame.games.models import Game

from .models import Guide


def DefaultView(request):
    guide_ids = Game.objects.values_list("published_guide_id", flat=True).distinct()
    guides = Guide.objects.filter(id__in=guide_ids)
    context = {"guides": guides}
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
