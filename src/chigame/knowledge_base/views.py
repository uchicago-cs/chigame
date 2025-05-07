from django.shortcuts import render

from chigame.games.models import Game

from .models import Guide


def DefaultView(request):
    guide_ids = Game.objects.values_list("published_guide_id", flat=True).distinct()
    guides = Guide.objects.filter(id__in=guide_ids)

    has_guides = False  # if the user hasn't uploaded any guide,
    # "manage your guide" button will not show up
    if request.user.is_authenticated:
        has_guides = Guide.objects.filter(author=request.user).exists()
    context = {"guides": guides, "has_guides": has_guides}
    return render(request, "knowledge-base/landing.html", context)


def ModeratorView(request):
    context = {}
    return render(request, "knowledge-base/moderator.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
