from django.shortcuts import render
from django.views.generic import ListView

from chigame.games.models import Game

from .models import Guide


class DefaultView(ListView):
    model = Guide
    template_name = "knowledge-base/landing.html"
    context_object_name = "guides"

    def get_queryset(self):
        guide_ids = Game.objects.values_list("published_guide_id", flat=True).distinct()
        return Guide.objects.filter(id__in=guide_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_guides"] = (
            self.request.user.is_authenticated and Guide.objects.filter(author=self.request.user).exists()
        )  # if the user hasn't uploaded any guide, "manage your guide" button will not show up
        return context


def ModeratorView(request):
    context = {}
    return render(request, "knowledge-base/moderator.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
