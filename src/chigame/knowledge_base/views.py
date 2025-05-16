# Keep model imports for now, as it will be required for WIP features
import markdown
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, ListView

from chigame.games.models import Category, Game

from .forms import MarkdownUploadForm
from .models import Guide, ReviewFeedback


# Viewers
class DefaultView(ListView):
    model = Guide
    template_name = "knowledge-base/landing.html"
    context_object_name = "guides"

    def get_queryset(self):
        guide_ids = Game.objects.values_list("published_guide_id", flat=True).distinct()
        queryset = Guide.objects.filter(id__in=guide_ids)

        query = self.request.GET.get("q")

        if query:
            # the query is originally on the game name of Guide object, and will
            # fail for queries like "Guide for [game name]"
            # here add queryset.annotate to make query for "Guide for..." works
            queryset = queryset.annotate(
                guide_title=Concat(Value("Guide for "), F("game_id__name"), output_field=CharField())
            ).filter(Q(guide_title__icontains=query) | Q(content__icontains=query))

        # for filtering; only support single-choice filtering for now
        category = self.request.GET.get("category")
        if category:
            categorymatch = Category.objects.get(name=category)
            queryset = queryset.filter(game__categories=categorymatch)

        # for sorting
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
        # make sure "manage my guide" only shows up when the user uploads
        # a guide previously
        context["has_guides"] = (
            self.request.user.is_authenticated and Guide.objects.filter(author=self.request.user).exists()
        )
        # to facilitate filtering
        context["categories"] = Category.objects.filter(
            id__in=Game.objects.values_list("categories", flat=True).distinct()
        )
        return context


class GuideDetail(DetailView):
    model = Guide
    template_name = "knowledge-base/guide_detail.html"
    context_object_name = "guide"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guide = self.get_object()

        context["published"] = False

        if guide.game_id.published_guide_id == guide:
            context["published"] = True
        return context


# Contributors
@login_required
def ContributorMdUpload(request, pk=None):
    if pk:
        guide = get_object_or_404(Guide, pk=pk)
    else:
        guide = None

    # if it's reupload, we will make the game field read-only on the form
    fixed_game = guide.game_id if guide else None
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
            messages.success(request, "Guide Uploaded Successfully!")
            return redirect("contributor-manage-guide")

    else:
        form = MarkdownUploadForm(fixed_game=fixed_game)

    context = {"form": form, "guide": pk}
    return render(request, "knowledge-base/contributor_upload.html", context)


class ContributorManageGuide(LoginRequiredMixin, ListView):
    model = Guide
    template_name = "knowledge-base/contributor_manage_guide.html"
    context_object_name = "guides"

    def get_queryset(self):
        guides = self.request.user.authored_guides.all()

        for guide in guides:
            guide.latest_feedback = None
            if guide.status != 0:
                latest_feedback = guide.feedbacks.all().order_by("-timestamp").first()
                guide.latest_feedback = latest_feedback

        return guides


@login_required
def DownloadGuide(request, pk):
    guide = get_object_or_404(Guide, pk=pk)
    if guide.author != request.user:
        raise PermissionDenied
    content = guide.content  # Assuming this is already Markdown or close to it

    filename = f"guide_{guide.pk}.md"
    response = HttpResponse(content, content_type="text/markdown")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class FeedbackDetail(LoginRequiredMixin, DetailView):
    model = ReviewFeedback
    template_name = "knowledge-base/feedback_detail.html"
    context_object_name = "feedback"

    def get_object(self, queryset=None):
        feedback = super().get_object(queryset)
        if feedback.guide_id.author != self.request.user:
            raise PermissionDenied
        return feedback


# Moderators
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


class ReviewPendingGuideView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Guide
    template_name = "knowledge-base/moderator_review_guide.html"
    context_object_name = "guide"

    def test_func(self):
        return self.request.user.moderator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guide = self.get_object()
        context["html_content"] = mark_safe(markdown.markdown(guide.content, extensions=["fenced_code", "tables"]))
        context["feedback"] = ""
        context["message"] = ""
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        feedback = request.POST.get("feedback", "")
        action = request.POST.get("action")
        message = ""
        if action in ["accept", "reject", "request_changes"]:
            status_map = {
                "accept": Guide.GuideStatus.ACCEPTED,
                "reject": Guide.GuideStatus.REJECTED,
                "request_changes": Guide.GuideStatus.REQUESTED_CHANGE,
            }
            self.object.status = status_map[action]
            self.object.save()
            ReviewFeedback.objects.create(
                reviewer=request.user,
                guide_id=self.object,
                status=status_map[action],
                comment=feedback,
            )
            if action == "accept":
                message = "Guide accepted."
            elif action == "reject":
                message = "Guide rejected."
            elif action == "request_changes":
                message = "Changes requested."
        context = self.get_context_data(object=self.object)
        context["feedback"] = feedback
        context["message"] = message

        return redirect("knowledge-base-moderator")
