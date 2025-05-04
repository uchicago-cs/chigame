# Keep model imports for now, as it will be required for WIP features
# from .models import *
from django.shortcuts import render


def DefaultView(request):
    context = {}
    return render(request, "knowledge-base/landing.html", context)


def ModeratorView(request):
    context = {}
    return render(request, "knowledge-base/moderator.html", context)


def ContributorView(request):
    context = {}
    return render(request, "knowledge-base/contributor.html", context)
