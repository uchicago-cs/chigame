# Keep model imports for now, as it will be required for WIP features
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .forms import MarkdownUploadForm
from .models import Guide


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


def ModeratorView(request):
    context = {}
    return render(request, "knowledge-base/moderator.html", context)


@login_required
def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)


@login_required
def ContributorMdUpload(request, pk=None):
    guide = get_object_or_404(Guide, pk=pk)

    # if it's reupload, we will make the game field read-only on the form
    fixed_game = guide.game_id if guide else None

    if request.method == "POST":
        form = MarkdownUploadForm(request.POST, request.FILES, fixed_game=fixed_game)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]

            # Read the file content (assume UTF-8 encoded Markdown)
            content = uploaded_file.read().decode("utf-8")

            game = form.cleaned_data["game"]  # assuming you're also choosing a game

            if guide:
                guide.content = content
                guide.status = 0
                guide.save()
            else:
                guide = Guide.objects.create(author=request.user, content=content, game_id=game, status=0)

    else:
        form = MarkdownUploadForm(fixed_game=fixed_game)

    context = {"form": form, "guide": pk}
    return render(request, "knowledge-base/contributor_upload.html", context)
