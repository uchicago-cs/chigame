from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from .models import FriendInvitation, UserProfile

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    slug_field = "user__id"
    slug_url_kwarg = "user_profile_id"


user_profile_detail_view = UserProfileDetailView.as_view()


@login_required
def send_friend_invitation(request, pk):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    if sender.id == receiver.id:
        messages.error(request, "You can't send friendship invitation to yourself")
        return redirect(reverse("users:redirect"))

    if sender.id != receiver.id:
        _, new = FriendInvitation.objects.get_or_create(sender=sender, receiver=receiver)
    if new:
        messages.success(request, "Friendship invitation sent successfully.")
    else:
        messages.info(request, "Friendship invitation already sent before.")
    return redirect(reverse("users:redirect"))


@login_required
def cancel_friendship(request, pk):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    num = None
    try:
        friendship = FriendInvitation.objects.get(sender=sender, receiver=receiver)
        num, _ = friendship.delete()
    except ObjectDoesNotExist:
        messages.error(request, "Something went wrong please try again later!")
    if num:
        messages.success(request, "Friendship invitation cancelled successfully.")
    else:
        messages.error(request, "Something went wrong please try again later!")

    return redirect(reverse("users:redirect"))


@login_required
def user_search_results(request):
    if request.method == "GET":
        email = request.GET.get("email")
        # Search for the user by email
        try:
            user = get_object_or_404(User, email=email)
            return redirect("users:user-profile", pk=user.pk)
        # Redirect to the user's profile page
        except Exception:
            messages.error(request, "User does not exist!")
            return redirect(reverse("users:redirect"))
        # Handle no email provided or user not found
        # You can add error handling or display a message here
    # Handle GET request or other cases
    # You can render a search results page or display a message
    # based on the search query
    return render(request, "search_results.html")
