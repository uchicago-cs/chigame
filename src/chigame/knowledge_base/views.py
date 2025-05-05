# Keep model imports for now, as it will be required for WIP features
# from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Guide


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


@login_required
def ModeratorView(request):
    pending_guides = Guide.objects.filter(status=0)
    context = {"pendingGuides": pending_guides}
    return render(request, "knowledge-base/moderator.html", context)


@login_required
def ReviewDetail(request, pk):
    pass  # to be completed, should display the guide info, and the approve/reject/request change button


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
