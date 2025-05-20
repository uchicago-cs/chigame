from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from chigame.games.models import Lobby, Player, Tournament

from .models import (
    FriendInvitation,
    FriendRequestNotification,
    Group,
    GroupInvitationNotification,
    MatchInvitationNotification,
    Notification,
    NotificationLabel,
    UserProfile,
)
from .tables import FriendsTable, UserTable

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"

    # In parameters, use UserPassesTestMixin and uncomment the following code to
    # give error message if an outside user tries to access your detail view.
    # def test_func(self):
    # return self.request.user == self.get_object()


user_detail_view = UserDetailView.as_view()


class BaseUserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


class NameUpdateView(BaseUserUpdateView):
    fields = ["name"]


class UsernameUpdateView(BaseUserUpdateView):
    fields = ["username"]


name_update_view = NameUpdateView.as_view()
username_update_view = UsernameUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


@login_required
def user_list(request):
    """
    Displays a list of all users in the database. Only accessible to admins.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: Rendered template with context using UserTable

    Raises:
        HttpResponseNotFound: If the user is not an admin
    """
    if request.user.is_staff:
        users = User.objects.all()
        table = UserTable(users)
        context = {"users": users, "table": table}

        # Add information about top ranking users, total points collected, etc.

        return render(request, "users/user_list.html", context)
    else:
        return HttpResponseNotFound("Access to link is restricted to admins")


def user_history(request, pk):
    """
    Displays a user's history of matches and tournaments.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user

    Returns:
        HttpResponse: Rendered template with user history context including
            - user: The user
            - match_count: The number of matches the user has played
            - match_wins: The number of matches the user has won
            - tournament_count: The number of tournaments the user has played
            - tournament_wins: The number of tournaments the user has won

    Raises:
        Http404: If the requested user profile does not exist
    """
    try:
        user = User.objects.get(pk=pk)

        match_count = Lobby.objects.filter(match_status=3, members__in=[user]).count()
        match_wins = Player.objects.filter(Q(user=user, outcome=Player.WIN) | Q(team=user, outcome=Player.WIN)).count()

        tournament_count = Tournament.objects.filter(
            tournament_end_date__lt=timezone.now(), players__in=[user]
        ).count()
        tournament_wins = Tournament.objects.filter(winners__in=[user]).count()

        return render(
            request,
            "users/user_history.html",
            {
                "user": user,
                "match_count": match_count,
                "match_wins": match_wins,
                "tournament_count": tournament_count,
                "tournament_wins": tournament_wins,
            },
        )
    except User.DoesNotExist:
        raise Http404("The user you are trying to access does not exist")


def user_profile_detail_view(request, pk):
    """
    Displays a user's profile and options for managing friends and
    friendship requests.

    Handles both viewing one's own profile and other users' profiles. If
    viewing another profile, will check friendship status and display
    pending friend requests between the current user and the user
    being viewed.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user whose profile is being viewed

    Returns:
        HttpResponse: Rendered template with user profile context including
            - object: UserProfile instance
            - is_friend: Boolean indicating friendship status
            - friendship_request: FriendInvitation instance (can be from target user
              to current user or current user to target user)

    Raises:
        Http404: If the requested user profile does not exist
    """
    if request.user.is_authenticated and request.user.pk == pk:
        # if user is accessing their own profile, create a profile if it doesn't exist
        profile = UserProfile.get_or_create_profile(request.user)
        return render(request, "users/userprofile_detail.html", {"profile": profile})
    else:
        # fetch another user's profile
        try:
            profile = get_object_or_404(UserProfile, user__pk=pk)
        except UserProfile.DoesNotExist:
            if User.objects.filter(pk=pk).exists():
                raise Http404("The user you are trying to access does not have their profile set up.")
            else:
                raise Http404("The user you are trying to access does not exist.")

    # for checking friendship and pending friend request status
    is_friend = None
    friendship_request = None
    target_user = get_object_or_404(User, pk=pk)
    if request.user.is_authenticated:
        # check friendship or pending invitation with the target user
        is_friend = target_user.friends.filter(pk=request.user.pk).exists()
        if not is_friend:
            curr_user = request.user
            friendship_request = (
                FriendInvitation.objects.filter(
                    Q(sender=target_user, receiver=curr_user, is_deleted=False)
                    | Q(sender=curr_user, receiver=target_user, is_deleted=False)
                )
                .order_by("-timestamp")
                .first()
            )

    # provide frontend profile + friendship status
    context = {"profile": profile, "is_friend": is_friend, "friendship_request": friendship_request}
    return render(request, "users/userprofile_detail.html", context=context)


@login_required
def send_friend_invitation(request, pk):
    """
    Send a friend invitation from the current user to another user.
    Handles creation or renewal of associated notifications.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user to send the friend invitation to

    Returns:
        HttpResponse: Redirects to the user's profile
        Error messages: When trying to send invitation to yourself or to someone
        who is already a friend or who has already requested you
    """
    # fetch the current user and the target user
    curr_user = User.objects.get(pk=request.user.id)
    other_user = User.objects.get(pk=pk)

    # if the current user and the target user are already friends, return an error
    if curr_user.friends.filter(pk=other_user.pk).exists():
        messages.error(request, "You are already friends with this user")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
    # if the current user is trying to send a friend request to themselves, return an error
    if curr_user.id == other_user.id:
        messages.error(request, "You can't send friendship invitation to yourself")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
    # check if the friendship invitation already exists
    invitation, new = FriendInvitation.objects.filter(
        Q(sender=curr_user, receiver=other_user, is_deleted=False)
        | Q(sender=other_user, receiver=curr_user, is_deleted=False)
    ).get_or_create(defaults={"sender": curr_user, "receiver": other_user, "is_deleted": False})
    if new:
        messages.success(request, "Friendship invitation sent successfully.")
        notification = Notification.objects.create(
            actor=invitation,
            receiver=other_user,
            type=Notification.FRIEND_REQUEST,
            message=Notification.DEFAULT_MESSAGES[Notification.FRIEND_REQUEST],
        )
    # if the other user has already sent a friend request, return an error
    elif invitation.sender.pk == other_user.pk:
        messages.info(request, "You already have a pending friend invitation from this profile.")
    # if the friendship invitation already exists, return an error
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
    """
    Cancel a sent friend invitation and mark related notifications as deleted.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the friend invitation

    Returns:
        HttpResponse: Redirects to the user's profile
        Error messages: When trying to cancel a non-existent invitation or if deleting
        the invitation fails
    """
    # fetch the current user and the target user
    sender = User.objects.get(pk=request.user.id)
    receiver = User.objects.get(pk=pk)
    try:
        # check if the friendship invitation exists
        friendship = FriendInvitation.objects.get(sender=sender, receiver=receiver, is_deleted=False)
        notification = Notification.objects.get_by_actor(friendship)
    except FriendInvitation.DoesNotExist:
        messages.error(request, "Friendship invitation does not exist")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
    except Notification.DoesNotExist:
        # If notification doesn't exist, create one and delete it immediately
        notification = Notification.objects.create(
            actor=friendship,
            receiver=receiver,
            type=Notification.FRIEND_REQUEST,
        )

    friendship.delete()
    notification.mark_as_deleted()
    messages.success(request, "Friendship invitation cancelled successfully.")

    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def accept_friend_invitation(request, pk):
    """
    Accept a received friend invitation and establish friendship.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the friend invitation

    Returns:
        HttpResponse: Redirects to the user's profile
        Error messages: When user is not the receiver of the invitation or if accepting
        the invitation fails or if the friendship invitation does not exist

    Raises:
        Http404: If deleting the notification fails
    """
    try:
        # fetch the friendship invitation
        friendship = FriendInvitation.objects.get(pk=pk)
        # check if the friendship invitation is not for the current user
        if friendship.receiver != request.user:
            messages.error(request, "You are not the receiver of this friend invitation")
            return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

        # get the related notification before accepting
        try:
            notification = Notification.objects.get_by_actor(friendship)
            # ensure the notification is deleted
            notification.mark_as_deleted()
        except Notification.DoesNotExist:
            # fine if no notification exists
            pass

        # accept the friendship invitation
        friendship.accept_invitation()
        messages.success(request, "Friend invitation accepted successfully")
        # delete the friendship invitation
        friendship.delete()
    except FriendInvitation.DoesNotExist:
        messages.error(request, "This friend invitation does not exist")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def decline_friend_invitation(request, pk):
    """
    Decline (delete) a received friend invitation.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the friend invitation

    Returns:
        HttpResponse: Redirects to the user's profile
        Error messages: When user is not the receiver of the invitation or if declining
        the invitation fails or if the friendship invitation does not exist
    """
    try:
        # fetch the friendship invitation
        friendship = FriendInvitation.objects.get(pk=pk)
        # check if the friendship invitation is not for the current user
        if friendship.receiver.pk != request.user.pk:
            messages.error(request, "You are not the receiver of this friend invitation ")
        else:
            # get the notification
            try:
                notification = Notification.objects.get_by_actor(friendship)
                # mark notification as deleted
                notification.mark_as_deleted()
            except Notification.DoesNotExist:
                # fine if no notification exists
                pass

            friendship.delete()
    except FriendInvitation.DoesNotExist:
        messages.error(request, "This friend invitation does not exist")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


def user_search_results(request):
    """
    Search for user profiles based on email or name.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: Rendered template with search results
    """
    query_input = request.GET.get("q")
    context = {"found": False, "query_type": "Users"}
    if query_input:
        profiles_list = UserProfile.objects.filter(
            Q(user__email__icontains=query_input) | Q(user__name__icontains=query_input)
        )
        if profiles_list.count() > 0:
            context["found"] = True
            context["object_list"] = profiles_list
    return render(request, "pages/search_results.html", context)


def notification_search_results(request):
    """
    Search for notifications based on message.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: Rendered template with search results
    """
    query_input = request.GET.get("q")
    context = {"found": False, "query_type": "Notifications"}
    if query_input:
        notifications_list = Notification.objects.filter_by_receiver(request.user).filter(
            message__icontains=query_input
        )
        if notifications_list.count() > 0:
            context["found"] = True
            context["object_list"] = notifications_list
    return render(request, "pages/search_results.html", context)


@login_required
def user_inbox_view(request, pk, category="inbox"):
    """
    Displays a user's inbox containing notifications. The user can only access
    their own inbox.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user

    Returns:
        HttpResponse: Rendered template with user inbox context including
            - pk: The primary key of the user
            - user: The user
            - notifications: The notifications in the user's inbox
            - default_notification_messages: The default notification messages
            for each notification type
    """

    if pk != request.user.pk:
        messages.error(request, "Not your inbox")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

    user = request.user

    if category and category in dict(Notification.CATEGORY_CHOICES):
        notifications = Notification.objects.filter_by_receiver(user).filter_by_category(category)
    else:
        notifications = Notification.objects.filter_by_receiver(user)

    default_notification_messages = Notification.DEFAULT_MESSAGES
    user_labels = NotificationLabel.objects.filter(user=user)
    context = {
        "pk": pk,
        "user": user,
        "notifications": notifications,
        "default_notification_messages": default_notification_messages,
        "labels": user_labels,
        "active_category": category,
        "category_choices": Notification.CATEGORY_CHOICES,
    }

    if pk == user.id:
        return render(request, "users/user_inbox.html", context)
    else:
        messages.error(request, "Not your inbox")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def remove_friend(request, pk):
    """
    Handle the process of a user removing another user from their friends list.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user to remove from the current user's friends list

    Returns:
        HttpResponse: Redirects to the current user's profile
        Error messages: When trying to remove a non-existent user or yourself or
        if removing the user fails
    """
    # check if the current user is not trying to remove themselves
    if request.user.pk != pk:
        try:
            # fetch the current user and the target user
            curr_user = User.objects.get(pk=request.user.pk)
            other_user = User.objects.get(pk=pk)
            # remove the users from each other's friends list
            curr_user.friends.remove(other_user)
            other_user.friends.remove(curr_user)
            messages.success(request, "Friend removed successfully")
            return redirect(reverse("users:user-profile", kwargs={"pk": pk}))
        except User.DoesNotExist:
            messages.error(request, "This user does not exist")
    else:
        messages.error(request, "You are not friends with yourself!")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def friend_list_view(request, pk):
    """
    Display a user's list of friends. Only accessible by the user themselves.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user

    Returns:
        HttpResponse: Rendered template with user friend list context
        Error messages: When trying to access another user's friend list

    Raises:
        Http404: If the requested user profile does not exist
    """
    # fetch the current user and the target user
    user = request.user
    target_user = get_object_or_404(User, pk=pk)
    # fetch the target user's friends
    friends = target_user.friends.all()
    # render the friends table
    table = FriendsTable(friends)
    context = {"table": table}
    # if the target user is the current user, render the friends list
    if pk == user.id:
        return render(request, "users/user_friend_list.html", context)
    else:
        messages.error(request, "Not your friend list!")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


def deleted_notifications_view(request, pk):
    """
    Display a user's list of deleted notifications. Only accessible by the user themselves.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user

    Returns:
        HttpResponse: Rendered template with user deleted notifications context
        Error messages: When trying to access another user's inbox
    """
    user = request.user
    notifications = Notification.objects.filter_by_receiver(user, deleted=True)
    default_notification_messages = Notification.DEFAULT_MESSAGES
    context = {
        "pk": pk,
        "user": user,
        "notifications": notifications,
        "default_notification_messages": default_notification_messages,
    }
    if pk == user.id:
        return render(request, "users/deleted_notifications.html", context)
    else:
        messages.error(request, "Not your inbox")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def notification_detail(request, pk):
    """
    Redirect the user based on a specific notification's action type (e.g., friend request, match invitation).

    Args:
        request (HttpRequest)
        pk (int): The primary key of the notification

    Returns:
        HttpResponse: Redirects to the appropriate page based on the notification type

    Raises:
        Http404: If the requested notification does not exist
    """
    try:
        notification = Notification.objects.get(pk=pk)
        if notification.receiver.pk != request.user.pk:
            messages.error(request, "You can not redirect from this notification")
            return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))
        notification.mark_as_read()

        if notification.type == Notification.FRIEND_REQUEST:
            handler = FriendRequestNotification(notification)
            return redirect(handler.get_redirect_str())
        elif notification.type == Notification.MATCH_INVITATION:
            handler = MatchInvitationNotification(notification)
            return redirect(handler.get_redirect_str())
        elif notification.type == Notification.GROUP_INVITATION:
            handler = GroupInvitationNotification(notification)
            return redirect(handler.get_redirect_str())
        else:
            raise NotImplementedError("No notification detail implemented for this notification type")
    except Notification.DoesNotExist:
        raise Http404("Notification does not exist")


@login_required
def act_on_inbox_notification(request, pk, action):
    """
    Allow a user to perform actions (mark as read/unread, delete) on a notification in their inbox.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the notification
        action (str): The action to perform on the notification

    Returns:
        HttpResponse: Redirects to the user's inbox
        Error messages: When trying to perform actions on a non-existent notification or
        when trying to perform actions on someone else's notifications
    """
    try:
        notification = Notification.objects.get(pk=pk)
        if notification.receiver.pk != request.user.pk:
            messages.error(request, "You can not perform actions on this notification")
            return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))
        if action == "mark_read":
            notification.mark_as_read()
        elif action == "mark_unread":
            notification.mark_as_unread()
        elif action == "delete":
            notification.mark_as_deleted()
        elif action == "move_to_inbox":
            notification.mark_as_unread()
    except Notification.DoesNotExist:
        messages.error(request, "Something went wrong. This notification does not exist")
    return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))


@login_required
def bulk_inbox(request):
    """
    Perform bulk operations (delete or mark as read) on multiple selected notifications.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: Redirects to the user's inbox
    """
    if request.method == "POST":
        selected_notifications = request.POST.getlist("notification[]")
        if "delete_all" in request.POST:
            for pk in selected_notifications:
                notification = Notification.objects.get(pk=pk)
                notification.mark_as_deleted()
        if "mark_all" in request.POST:
            for pk in selected_notifications:
                notification = Notification.objects.get(pk=pk)
                notification.mark_as_read()
    return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))


@login_required
def bookmark_notification(request, pk):
    try:
        notification = Notification.objects.get(pk=pk)
        if notification.receiver != request.user:
            messages.error(request, "This notification is not yours. You can not bookmark it.")
        else:
            notification.bookmarked = not notification.bookmarked
            notification.save()
            status_msg = "Bookmarked" if notification.bookmarked else "Un-bookmarked"
            messages.success(request, f"Notification {status_msg.lower()}.")
    except Notification.DoesNotExist:
        messages.error(request, "Notification does not exist.")

    return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))


@login_required
def view_bookmarked_notifications(request, pk):
    user = request.user
    notifications = Notification.objects.filter_by_receiver(user).filter(bookmarked=True)
    default_notification_messages = Notification.DEFAULT_MESSAGES
    context = {
        "pk": pk,
        "user": user,
        "notifications": notifications,
        "default_notification_messages": default_notification_messages,
    }
    if pk == user.id:
        return render(request, "users/bookmarked_notifications.html", context)
    else:
        messages.error(request, "Not your inbox")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def upload_profile_photo(request):
    if request.method == "POST" and request.FILES.get("photo"):
        profile = UserProfile.get_or_create_profile(request.user)
        profile.profile_photo = request.FILES["photo"]
        profile.save()
        messages.success(request, "Profile photo updated.")
    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@csrf_protect
@require_POST
def move_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, receiver=request.user)
    new_category = request.POST.get("category")
    if new_category and new_category in dict(Notification.CATEGORY_CHOICES):
        notification.category = new_category
        notification.save()
        messages.success(request, f"Notification moved to {new_category}.")
        return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))

    label_id = request.POST.get("label_id")
    if label_id:
        try:
            label = NotificationLabel.objects.get(pk=label_id, user=request.user)
            notification.labels.add(label)
            messages.success(request, "Label assigned to notification.")
        except NotificationLabel.DoesNotExist:
            messages.error(request, "Label not found or does not belong to you.")
        return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))

    messages.error(request, "Invalid category or label.")
    return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))


@login_required
def create_notification_label(request):
    """
    Handles the creation of a new notification label for the logged-in user.

    If the request method is POST and a label name is provided, it creates a new
    NotificationLabel object associated with the user. If the label name is empty,
    it displays an error message. Finally, it redirects the user back to their inbox.
    """
    if request.method == "POST":
        label_name = request.POST.get("label_name")
        if label_name:
            NotificationLabel.objects.get_or_create(user=request.user, name=label_name)
            messages.success(request, "Label created successfully.")
        else:
            messages.error(request, "Label name cannot be empty.")
    return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))


@login_required
def assign_label_to_notification(request, notification_id):
    """
    Assigns a selected notification label to a specific notification.

    It retrieves the notification and the label based on their IDs and ensures
    that both belong to the logged-in user. If the label is found, it's added
    to the notification's labels. If the label doesn't exist or doesn't belong
    to the user, an error message is displayed. The user is then redirected
    back to their inbox.

    Args:
        notification_id (int): The ID of the notification to assign the label to.
    """
    notification = get_object_or_404(Notification, pk=notification_id, receiver=request.user)
    label_id = request.POST.get("label_id")

    try:
        label = NotificationLabel.objects.get(pk=label_id, user=request.user)
        notification.labels.add(label)
        messages.success(request, "Label assigned to notification.")
    except NotificationLabel.DoesNotExist:
        messages.error(request, "Label not found or does not belong to you.")

    return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))


@login_required
def notifications_by_label(request, label_id):
    """
    Retrieves and displays all notifications associated with a specific label
    belonging to the logged-in user.

    It fetches the NotificationLabel object and then retrieves all notifications
    that have been assigned this label. These are then passed to a template for
    rendering.

    Args:
        label_id (int): The ID of the notification label to filter by.
    """
    label = get_object_or_404(NotificationLabel, pk=label_id, user=request.user)
    notifications = label.notifications.all()
    context = {
        "label": label,
        "notifications": notifications,
    }
    return render(request, "users/notifications_by_label.html", context)


class GroupListView(ListView):
    model = Group
    template_name = "users/group_list.html"


class GroupDetailView(DetailView):
    model = Group
    template_name = "users/group_detail.html"
