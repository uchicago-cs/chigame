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
from .tables import UserTable

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

@login_required
def user_list(request):
    users = User.objects.all()
    table = UserTable(users)
    context = {"users": users, "table": table}

    return render(request, "users/user_list.html", context)

@login_required
def user_detail(request):
    users = User.objects.all()

    return render(request, "users/user_detail.html", {"users": users})

def user_profile_detail_view(request, pk):
    try:
        profile = get_object_or_404(UserProfile, user__pk=pk)
        is_friend = profile.friends.filter(pk=request.user.pk).exists()
        friendship_request = None
        if not is_friend:
            friendship_request = FriendInvitation.objects.filter(sender=request.user.pk, receiver=pk).exists()
        context = {"object": profile, "is_friend": is_friend, "friendship_request": friendship_request}
        return render(request, "users/userprofile_detail.html", context=context)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile does not exist")
        return redirect(reverse("users:detail", kwargs={"pk": request.user.pk}))


@login_required
def send_friend_invitation(request, pk):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    if sender.id == receiver.id:
        messages.error(request, "You can't send friendship invitation to yourself")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
    if sender.id != receiver.id:
        _, new = FriendInvitation.objects.get_or_create(sender=sender, receiver=receiver)
    if new:
        messages.success(request, "Friendship invitation sent successfully.")
    else:
        messages.info(request, "Friendship invitation already sent before.")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def cancel_friend_invitation(request, pk):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    num = None
    try:
        friendship = FriendInvitation.objects.get(sender=sender, receiver=receiver)
        num, _ = friendship.delete()
    except ObjectDoesNotExist:
        messages.error(request, "Friendship invitation does not exist")
    if num:
        messages.success(request, "Friendship invitation cancelled successfully.")
    else:
        messages.error(request, "Something went wrong please try again later!")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

