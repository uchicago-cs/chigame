from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from rest_framework import status
from rest_framework.response import Response

from .models import FriendInvitation, Notification, UserProfile
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

    # Add information about top ranking users, total points collected, etc.

    return render(request, "users/user_list.html", context)


@login_required
def user_detail(request):
    users = User.objects.all()

    # Shows a user detail page if logged in as a user
    # Shows a list of all users if logged in as admin

    return render(request, "users/user_detail.html", {"users": users})


def user_history(request, pk):
    try:
        user = User.objects.get(pk=pk)

        return render(request, "users/user_history.html", {"user": user})
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


def user_profile_detail_view(request, pk):
    try:
        profile = get_object_or_404(UserProfile, user__pk=pk)
        if request.user.pk == pk:
            return render(request, "users/userprofile_detail.html", {"object": profile})
        is_friend = None
        friendship_request = None
        if request.user.pk:
            is_friend = profile.friends.filter(pk=request.user.pk).exists()
            if not is_friend:
                curr_user = User.objects.get(pk=request.user.id)
                other_user = profile.user
                friendship_request = FriendInvitation.objects.filter(
                    Q(sender=curr_user, receiver=other_user) | Q(sender=other_user, receiver=curr_user)
                ).first()
        context = {"object": profile, "is_friend": is_friend, "friendship_request": friendship_request}
        return render(request, "users/userprofile_detail.html", context=context)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile does not exist")
        return redirect(reverse("users:detail", kwargs={"pk": request.user.pk}))


@login_required
def send_friend_invitation(request, pk):
    curr_user = User.objects.get(pk=request.user.id)
    other_user = User.objects.get(pk=pk)
    if curr_user.id == other_user.id:
        messages.error(request, "You can't send friendship invitation to yourself")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

    invitation, new = FriendInvitation.objects.filter(
        Q(sender=curr_user, receiver=other_user) | Q(sender=other_user, receiver=curr_user)
    ).get_or_create(defaults={"sender": curr_user, "receiver": other_user})
    if new:
        messages.success(request, "Friendship invitation sent successfully.")
        notification = Notification.objects.create(
            actor=invitation, receiver=other_user, type=Notification.FRIEND_REQUEST
        )
    elif invitation.sender.pk == other_user.pk:
        messages.info(request, "You already have a pending friend invitation from this profile.")
    else:
        messages.info(request, "Friendship invitation already sent before.")
        try:
            notification = Notification.objects.get_by_actor(invitation, receiver=other_user)
            notification.renew_notification()
        except Notification.DoesNotExist:
            notification = Notification.objects.create(
                actor=invitation, receiver=other_user, type=Notification.FRIEND_REQUEST
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
def accept_friend_invitation(request, pk):
    try:
        friendship = FriendInvitation.objects.get(pk=pk)
        if friendship.receiver.pk != request.user.pk:
            messages.error(request, "You are not the receiver of this friend invitation ")
        else:
            friendship.accept_invitation()
    except FriendInvitation.DoesNotExist:
        messages.error(request, "This friend invitation does not exist")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def decline_friend_invitation(request, pk):
    try:
        friendship = FriendInvitation.objects.get(pk=pk)
        if friendship.receiver.pk != request.user.pk:
            messages.error(request, "You are not the receiver of this friend invitation ")
        else:
            friendship.delete()
    except FriendInvitation.DoesNotExist:
        messages.error(request, "This friend invitation does not exist")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


def user_search_results(request):
    query = request.GET.get("query")
    context = {"nothing_found": True, "query_type": "Users"}
    if query:
        users_list = UserProfile.objects.filter(Q(user__email__icontains=query) | Q(user__name__icontains=query))
        if users_list.count() > 0:
            context.pop("nothing_found")
            context["object_list"] = users_list
    return render(request, "pages/search_results.html", context)


@login_required
def user_inbox_view(request, pk):
    user = request.user
    notifications = Notification.objects.filter(receiver=user)
    context = {"pk": pk, "user": user, "notifications": notifications}
    if pk == user.id:
        return render(request, "users/user_inbox.html", context)
    else:
        messages.error(request, "Not your inbox")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def friend_list_view(request, pk):
    user = request.user
    profile = get_object_or_404(UserProfile, user__pk=pk)
    friends = profile.friends
    context = {"pk": pk, "user": user, "friends": friends, "profile": profile}
    if pk == user.id:
        return render(request, "users/user_friend_list.html", context)
    else:
        messages.error(request, "Not your friend list!")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
