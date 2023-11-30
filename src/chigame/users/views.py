from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from .models import FriendInvitation, Notification, UserProfile, GameInvitation, TournamentInvitation
from chigame.games.models import Match, Tournament

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
        friend_request, new = FriendInvitation.objects.get_or_create(sender=sender, receiver=receiver)

    if new:
        messages.success(request, "Friendship invitation sent successfully.")
        notification = Notification.objects.create(
            actor=friend_request, receiver=receiver, type=Notification.FRIEND_REQUEST
        )
    else:
        messages.info(request, "Friendship invitation already sent before.")
        try:
            notification = Notification.objects.get_by_actor(friend_request, receiver=receiver)
            notification.renew_notification()
        except Notification.DoesNotExist:
            notification = Notification.objects.create(
                actor=friend_request, receiver=receiver, type=Notification.FRIEND_REQUEST
            )
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def cancel_friend_invitation(request, pk):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    num = None
    try:
        friendship = FriendInvitation.objects.get(sender=sender, receiver=receiver)
        notification = Notification.objects.get_by_actor(friendship)
    except FriendInvitation.DoesNotExist:
        messages.error(request, "Friendship invitation does not exist")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
    except Notification.DoesNotExist:
        notification = Notification.objects.create(
            actor=friendship, receiver=receiver, type=Notification.FRIEND_REQUEST
        )
        notification.mark_as_deleted()
    num, _ = friendship.delete()
    notification.mark_as_deleted()
    if num:
        messages.success(request, "Friendship invitation cancelled successfully.")
    else:
        messages.error(request, "Something went wrong please try again later!")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def remove_friend(request, pk):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    sender_profile = sender.profile
    sender_profile.friends.remove(receiver)
    messages.success(request, "Friend removed successfully.")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

@login_required
def invite_to_game(request, pk, match_id):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    match = Match.objects.get(pk=match_id)  
    GameInvitation.objects.create(sender=sender, receiver=receiver, match=match)
    messages.success(request, "Invitation to game sent successfully.")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

@login_required
def invite_to_tournament(request, pk, tournament_id):
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    tournament = Tournament.objects.get(pk=tournament_id) 
    TournamentInvitation.objects.create(sender=sender, receiver=receiver, tournament=tournament)
    messages.success(request, "Invitation to tournament sent successfully.")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
