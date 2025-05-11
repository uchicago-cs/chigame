# Keep model imports for now, as it will be required for WIP features
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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


@login_required
def ContributorManageGuide(request):
    guides = request.user.authored_guides.all()
    context = {"guides": guides}
    return render(request, "knowledge-base/contributor_manage_guide.html", context)


@login_required
def DownloadGuide(request, pk):
    guide = get_object_or_404(Guide, pk=pk)
    content = guide.content  # Assuming this is already Markdown or close to it

    filename = f"guide_{guide.pk}.md"
    response = HttpResponse(content, content_type="text/markdown")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
