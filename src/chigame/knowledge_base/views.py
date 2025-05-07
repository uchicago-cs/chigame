from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat
from django.shortcuts import render
from django.views.generic import ListView

from chigame.games.models import Category, Game

from .models import Guide


class DefaultView(ListView):
    model = Guide
    template_name = "knowledge-base/landing.html"
    context_object_name = "guides"

    def get_queryset(self):
        guide_ids = Game.objects.values_list("published_guide_id", flat=True).distinct()
        queryset = Guide.objects.filter(id__in=guide_ids)

        query = self.request.GET.get("q")

        if query:
            # add queryset.annotate to make query for "Guide for Game A" works
            queryset = queryset.annotate(
                guide_title=Concat(Value("Guide for "), F("game_id__name"), output_field=CharField())
            ).filter(Q(guide_title__icontains=query) | Q(content__icontains=query))

        category = self.request.GET.get("category")
        if category:
            categorymatch = Category.objects.get(name=category)
            queryset = queryset.filter(game__categories=categorymatch)

        sort = self.request.GET.get("sort")
        if sort == "az":
            queryset = queryset.order_by("game__name")
        elif sort == "za":
            queryset = queryset.order_by("-game__name")
        elif sort == "old":
            queryset = queryset.order_by("recent_upload")
        else:  # default: newest first
            queryset = queryset.order_by("-recent_upload")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_guides"] = (
            self.request.user.is_authenticated and Guide.objects.filter(author=self.request.user).exists()
        )  # if the user hasn't uploaded any guide, "manage your guide" button will not show up
        context["categories"] = Category.objects.filter(
            id__in=Game.objects.values_list("categories", flat=True).distinct()
        )
        return context


def ModeratorView(request):
    context = {}
    return render(request, "knowledge-base/moderator.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
