from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MarkdownUploadForm
from .models import Guide


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


def ModeratorView(request):
    context = {}
    return render(request, "knowledge-base/moderator.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)


@login_required
def ContributorMdUpload(request, pk=None):
    # if it's reupload, we will retrieve the guide and edit fixed_game to
    # make the game field appear read-only on the form
    if pk:
        guide = get_object_or_404(Guide, pk=pk)
        # disallow user to access url if they don't access the guide or the guide
        # status is not change requested
        if guide.author != request.user or guide.status != 3:
            raise PermissionDenied
        fixed_game = guide.game_id
    else:
        guide = None
        fixed_game = None

    if request.method == "POST":
        form = MarkdownUploadForm(request.POST, request.FILES, fixed_game=fixed_game)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]

            # Read the file content (assume UTF-8 encoded Markdown)
            content = uploaded_file.read().decode("utf-8")

            # when reupload
            if guide:
                guide.content = content
                guide.status = 0
                guide.save()
            # when upload
            else:
                game = form.cleaned_data["game"]  # the game user chooses
                guide = Guide.objects.create(author=request.user, content=content, game_id=game, status=0)
        return redirect("knowledge-base")
        # I make it redirects to landing page after submission for now, could later
        # create an issue that adds a "sucessful submission" page

    else:
        form = MarkdownUploadForm(fixed_game=fixed_game)

    context = {"form": form, "guide": pk}
    return render(request, "knowledge-base/contributor_upload.html", context)
