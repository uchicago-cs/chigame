# Keep model imports for now, as it will be required for WIP features
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .models import Guide


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


def GuideDetailView(request, pk):
    guide = get_object_or_404(Guide, pk=pk)
    context = {"guide": guide}
    return render(request, "knowledge-base/guide_detail.html", context)


class ModeratorGuidesPending(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Guide
    template_name = "knowledge-base/moderator_pending_guides.html"
    context_object_name = "pendingGuides"

    def get_queryset(self):
        queryset = Guide.objects.filter(status=0)

        # for sorting
        sort = self.request.GET.get("sort")
        if sort == "old":
            queryset = queryset.order_by("recent_upload")
        else:  # default: newest first
            queryset = queryset.order_by("-recent_upload")

        return queryset

    # called when UserPassesTestMixin
    # this makes sure only moderators can access this page
    def test_func(self):
        return self.request.user.moderator


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
