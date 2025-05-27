from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, RedirectView, UpdateView, View
from django.views.generic.edit import CreateView, DeleteView
from django_tables2 import SingleTableView

from chigame.games.models import Game, GameList, Lobby, Player, Tournament

from .forms import FriendInvitationForm, UserProfileForm
from .models import (
    FriendInvitation,
    FriendRequestNotification,
    Group,
    GroupInvitation,
    GroupInvitationNotification,
    MatchInvitationNotification,
    Notification,
    NotificationLabel,
    UserProfile,
)
from .tables import GroupTable, UserTable

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["profile"] = self.request.user.userprofile
        except UserProfile.DoesNotExist:
            context["profile"] = None
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            profile = self.request.user.userprofile
            profile.bio = self.request.POST.get("bio", profile.bio)
            profile.save()
        except UserProfile.DoesNotExist:
            pass
        return response


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

    IMPORTANT NOTE TO DEVELOPERS: Profile url takes user pk, not profile pk.
    It might not necessarily be the case that providing profile pk will get you
    the profile of the user you want.

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
        # Get favorite games from GameList system
        favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=request.user)
        favorite_games = favorites_list.games.all()
        available_games = Game.objects.exclude(id__in=favorite_games.values_list("id", flat=True))
        return render(
            request,
            "users/userprofile_detail.html",
            {"profile": profile, "available_games": available_games, "favorite_games": favorite_games},
        )
    else:
        # fetch another user's profile
        try:
            profile = get_object_or_404(UserProfile, user__pk=pk)
        except UserProfile.DoesNotExist:
            if User.objects.filter(pk=pk).exists():
                raise Http404("The user you are trying to access does not have their profile set up.")
            else:
                raise Http404("The user you are trying to access does not exist.")

    # Get favorite games for the profile user (for viewing other users' profiles)
    try:
        favorites_list = GameList.objects.get(name="Favorites", created_by=profile.user)
        favorite_games = favorites_list.games.all()
    except GameList.DoesNotExist:
        favorite_games = []

    # for checking friendship and pending friend request status
    is_friend = None
    friendship_request = None
    is_blocked = False
    friend_request_message = None
    target_user = get_object_or_404(User, pk=pk)
    if request.user.is_authenticated:
        # check friendship or pending invitation with the target user
        is_friend = target_user.friends.filter(pk=request.user.pk).exists()
        # check if current user has blocked the target user
        is_blocked = request.user.blocked_users.filter(pk=target_user.pk).exists()
        if not is_friend:
            curr_user = request.user
            friendship_request = FriendInvitation.objects.get_by_users(curr_user, target_user)
            # If there's a pending personalized friend request from the profile owner to current user, get the message
            if friendship_request and friendship_request.sender == target_user and friendship_request.message:
                friend_request_message = friendship_request.message

    # provide frontend profile + friendship status
    context = {
        "profile": profile,
        "is_friend": is_friend,
        "friendship_request": friendship_request,
        "favorite_games": favorite_games,
        "is_blocked": is_blocked,
        "friend_request_message": friend_request_message,
    }
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

    # Check if either user has blocked the other
    if curr_user.blocked_users.filter(pk=other_user.pk).exists():
        messages.error(request, "You have blocked this user.")
        return redirect(reverse("users:user-profile", kwargs={"pk": pk}))
    if other_user.blocked_users.filter(pk=curr_user.pk).exists():
        messages.error(request, "User not found.")
        return redirect(reverse("users:user-profile", kwargs={"pk": pk}))

    # if the current user and the target user are already friends, return an error
    if curr_user.friends.filter(pk=other_user.pk).exists():
        messages.error(request, "You are already friends with this user")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
    # if the current user is trying to send a friend request to themselves, return an error
    if curr_user.id == other_user.id:
        messages.error(request, "You can't send friendship invitation to yourself")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))
    # check if the friendship invitation already exists
    invitation = FriendInvitation.objects.filter(
        Q(sender=curr_user, receiver=other_user, is_deleted=False)
        | Q(sender=other_user, receiver=curr_user, is_deleted=False)
    ).first()

    if invitation:
        # if the other user has already sent a friend request it throws an error
        if invitation.sender.pk == other_user.pk:
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

    # Check if user wants to add the optional message
    show_form = request.GET.get("with_message") == "true" or (
        request.method == "GET" and "with_message" in request.GET
    )

    if request.method == "GET" and show_form:
        form = FriendInvitationForm()
        context = {
            "form": form,
            "target_user": other_user,
        }
        return render(request, "users/send_friend_invitation.html", context)

    elif request.method == "POST":
        form = FriendInvitationForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data.get("message", "")
        else:
            context = {
                "form": form,
                "target_user": other_user,
            }
            return render(request, "users/send_friend_invitation.html", context)
    else:
        message = ""

    new_invitation = FriendInvitation.objects.create(
        sender=curr_user, receiver=other_user, message=message, is_deleted=False
    )

    messages.success(request, "Friendship invitation sent successfully.")

    # Create notification using default friend request message
    content_type = ContentType.objects.get_for_model(FriendInvitation)

    notification, new = Notification.objects.get_or_create(
        actor_content_type=content_type,
        actor_object_id=new_invitation.id,
        receiver=other_user,
        type=Notification.FRIEND_REQUEST,
        defaults={"message": Notification.DEFAULT_MESSAGES[Notification.FRIEND_REQUEST]},
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
            Q(user__username__icontains=query_input) | Q(user__name__icontains=query_input)
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
    Display the user's inbox with categorized notifications.

    This view renders the inbox page for the logged-in user, showing notifications
    filtered by the specified category. It ensures that users can only access their
    own inbox and redirects otherwise.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): The primary key of the user whose inbox is being accessed.
        category (str, optional): The category of notifications to display.
            Defaults to "inbox". Special category "deleted" is also handled.

    Returns:
        HttpResponse: The rendered inbox page with the filtered notifications.
    """
    if pk != request.user.pk:
        messages.error(request, "Not your inbox")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

    user = request.user

    # Handle deleted notifications
    if category == "deleted":
        notifications = Notification.objects.filter_by_receiver(user, deleted=True)
    elif category and category in dict(Notification.CATEGORY_CHOICES):
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

    return render(request, "users/user_inbox.html", context)


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
    context = {"friends": friends}

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
    """
    # Get the category to return to, defaulting to 'inbox'
    next_category = request.GET.get("next", "inbox")

    try:
        notification = Notification.objects.get(pk=pk)
        if notification.receiver.pk != request.user.pk:
            messages.error(request, "You can not perform actions on this notification")
            return redirect(
                reverse("users:user-inbox-category", kwargs={"pk": request.user.pk, "category": next_category})
            )

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

    return redirect(reverse("users:user-inbox-category", kwargs={"pk": request.user.pk, "category": next_category}))


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
    """
    Handle user actions to move a notification to a different category
    or assign a label to it.

    This view supports POST requests to:
    - Change the category of a notification (e.g., move to "archived").
    - Assign an existing label to the notification.

    It validates that the notification belongs to the requesting user
    and provides appropriate feedback messages.

    Args:
        request (HttpRequest): The incoming POST request containing category or label_id.
        pk (int): The primary key of the notification to be modified.

    Returns:
        HttpResponseRedirect: Redirects to the user's inbox view under the target category.
    """
    notification = get_object_or_404(Notification, pk=pk, receiver=request.user)
    new_category = request.POST.get("category")
    next_category = request.POST.get("next") or "inbox"  # fallback to inbox if not provided

    if new_category and new_category in dict(Notification.CATEGORY_CHOICES):
        notification.category = new_category
        notification.save()
        # messages.success(request, f"Notification moved to {new_category}.") # Message Location needs to be fixed
        return redirect("users:user-inbox-category", pk=request.user.pk, category=next_category)

    label_id = request.POST.get("label_id")
    if label_id:
        try:
            label = NotificationLabel.objects.get(pk=label_id, user=request.user)
            notification.labels.add(label)
            messages.success(request, "Label assigned to notification.")
        except NotificationLabel.DoesNotExist:
            messages.error(request, "Label not found or does not belong to you.")
        return redirect("users:user-inbox-category", pk=request.user.pk, category=next_category)

    messages.error(request, "Invalid category or label.")
    return redirect("users:user-inbox-category", pk=request.user.pk, category=next_category)


@login_required
def create_notification_label(request):
    """
    Create a custom notification label for the logged-in user.

    This view handles POST requests to add user-defined (custom) labels,
    which can be used to organize and filter notifications. If a label with
    the given name already exists for the user, a message is shown instead.

    Args:
        request (HttpRequest): The POST request containing 'label_name' in the form data.

    Returns:
        HttpResponseRedirect: Redirects to the label management page after processing.
    """
    if request.method == "POST":
        label_name = request.POST.get("label_name")
        if label_name:
            label, created = NotificationLabel.objects.get_or_create(user=request.user, name=label_name)
            if created:
                messages.success(request, f"Label '{label_name}' created successfully.")
            else:
                messages.info(request, f"Label '{label_name}' already exists.")
        else:
            messages.error(request, "Label name cannot be empty.")
    return redirect(reverse("users:manage-labels-page"))


@login_required
def manage_labels_page_view(request):
    """
    Render the label management page for custom notification labels.

    Displays all user-defined labels associated with the logged-in user,
    allowing them to review and manage their custom organization of notifications.

    Args:
        request (HttpRequest): The incoming GET request from the logged-in user.

    Returns:
        HttpResponse: Renders the 'manage_labels.html' template with the user's labels.
    """
    user_labels = NotificationLabel.objects.filter(user=request.user).order_by("name")
    context = {
        "labels": user_labels,
    }
    return render(request, "users/manage_labels.html", context)


@login_required
@require_POST
def delete_notification_label(request, label_id):
    """
    Delete a custom notification label belonging to the logged-in user.

    This view handles POST requests to remove a user-defined label by ID.
    It ensures the label belongs to the requesting user before deletion.
    After deletion, the user is redirected to the label management page
    with a success message.

    Args:
        request (HttpRequest): The incoming POST request from the user.
        label_id (int): The primary key of the custom label to delete.

    Returns:
        HttpResponseRedirect: Redirects to the label management page with a status message.
    """
    label = get_object_or_404(NotificationLabel, pk=label_id, user=request.user)
    label_name = label.name

    label.delete()

    messages.success(request, f"Label '{label_name}' deleted successfully.")
    return redirect(reverse("users:manage-labels-page"))


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
        messages.error(request, "Label not  found or does not belong to you.")

    return redirect(reverse("users:user-inbox", kwargs={"pk": request.user.pk}))


@login_required
def notifications_by_label(request, label_id):
    """
    Display all non-deleted notifications associated with a specific custom label.

    This view retrieves notifications tagged with a user-defined label, belonging
    to the logged-in user. Deleted notifications are excluded from the result.
    It also passes all of the user's labels to the template for sidebar display.

    Args:
        request (HttpRequest): The incoming GET request from the logged-in user.
        label_id (int): The primary key of the custom label used to filter notifications.

    Returns:
        HttpResponse: Renders the 'notifications_by_label.html' template with filtered notifications.
    """
    label = get_object_or_404(NotificationLabel, pk=label_id, user=request.user)
    # Fetch only visible (non-deleted) notifications for the current user that have this label
    notifications = label.notifications.filter(receiver=request.user, visible=True).order_by("-first_sent")

    all_user_labels = NotificationLabel.objects.filter(user=request.user).order_by("name")

    context = {
        "label": label,
        "notifications": notifications,
        "active_category": f"label-{label.id}",
        "category_choices": Notification.CATEGORY_CHOICES,
        "labels": all_user_labels,
        "pk": request.user.pk,
    }
    return render(request, "users/notifications_by_label.html", context)


@login_required
def blocked_users_list(request):
    """
    Display a list of users that the current user has blocked.

    Args:
        request (HttpRequest)

    Returns:
        HttpResponse: Rendered template with blocked users list
    """
    current_user = request.user
    blocked_users = current_user.blocked_users.all()

    context = {
        "blocked_users": blocked_users,
        "user": current_user,
    }

    return render(request, "users/blocked_users_list.html", context)


@login_required
def unblock_user(request, pk):
    """
    Unblock a previously blocked user.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user to unblock

    Returns:
        HttpResponse: Redirects to the blocked users list
    """
    try:
        user_to_unblock = User.objects.get(pk=pk)
        current_user = request.user

        if current_user.blocked_users.filter(pk=user_to_unblock.pk).exists():
            current_user.blocked_users.remove(user_to_unblock)
            messages.success(request, f"You have unblocked {user_to_unblock.name or user_to_unblock.email}.")
        else:
            messages.info(request, "This user is not blocked.")

    except User.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect(reverse("users:blocked-users-list"))


@login_required
def toggle_profanity(request, pk):
    """
    Toggle the profanity filter for a user profile.
    """
    user = get_object_or_404(User, pk=pk)
    user.profanity_filter = not user.profanity_filter
    user.save()
    return redirect(reverse("users:user-profile", kwargs={"pk": pk}))


@require_POST
def add_favorite_game(request, game_id):
    """
    Add a game to the user's favorite games list.

    Args:
        request (HttpRequest): The HTTP request
        game_id (int): The ID of the game to add

    Returns:
        Redirects back to the user's profile
    """
    try:
        game = Game.objects.get(id=game_id)
        favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=request.user)
        favorites_list.games.add(game)
        messages.success(request, f"{game.name} added to your favorite games.")
    except Game.DoesNotExist:
        messages.error(request, "Game not found.")
    except Exception as e:
        messages.error(request, f"Error adding game to favorites: {str(e)}")

    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
@require_POST
def remove_favorite_game(request, game_id):
    """
    Remove a game from the user's favorite games list.

    Args:
        request (HttpRequest): The HTTP request
        game_id (int): The ID of the game to remove

    Returns:
        Redirects back to the user's profile
    """
    try:
        game = Game.objects.get(id=game_id)
        favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=request.user)
        favorites_list.games.remove(game)
        messages.success(request, f"{game.name} removed from your favorite games.")
    except Game.DoesNotExist:
        messages.error(request, "Game not found.")
    except Exception as e:
        messages.error(request, f"Error removing game from favorites: {str(e)}")

    return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))


@login_required
def block_user(request, pk):
    """
    Block a user to prevent them from sending friend invitations.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user to block

    Returns:
        HttpResponse: Redirects to the user's profile
    """
    try:
        user_to_block = User.objects.get(pk=pk)
        current_user = request.user

        if user_to_block == current_user:
            messages.error(request, "You cannot block yourself.")
            return redirect(reverse("users:user-profile", kwargs={"pk": current_user.pk}))

        # Remove friendship if they are friends
        if current_user.friends.filter(pk=user_to_block.pk).exists():
            current_user.friends.remove(user_to_block)

        # Cancel any pending friend invitations between them
        FriendInvitation.objects.filter(
            Q(sender=current_user, receiver=user_to_block, is_deleted=False)
            | Q(sender=user_to_block, receiver=current_user, is_deleted=False)
        ).update(is_deleted=True)

        # Block the user
        current_user.blocked_users.add(user_to_block)
        messages.success(request, f"You have blocked {user_to_block.name or user_to_block.email}.")

    except User.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect(reverse("users:user-profile", kwargs={"pk": pk}))


@login_required
def edit_profile(request, pk):
    """
    View for editing user profile information including bio.
    """
    if request.user.pk != pk:
        messages.error(request, "You can only edit your own profile.")
        return redirect("users:user-profile", pk=request.user.pk)

    profile = UserProfile.get_or_create_profile(request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("users:user-profile", pk=request.user.pk)
    else:
        form = UserProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "users/edit_profile.html", context)


@login_required
@require_POST
@csrf_protect
def unassign_label_from_notification(request, notification_id, label_id):
    """
    Remove a custom label from a specific notification for the logged-in user.

    This view handles POST requests to unassign a user-defined label from a
    notification, ensuring both belong to the current user. It provides
    success, info, or error messages based on the state of the label assignment.

    Args:
        request (HttpRequest): The POST request to unassign a label.
        notification_id (int): The ID of the notification to modify.
        label_id (int): The ID of the label to remove from the notification.

    Returns:
        HttpResponseRedirect: Redirects to the 'notifications-by-label' view for the same label.
    """
    notification = get_object_or_404(Notification, pk=notification_id, receiver=request.user)

    try:
        # Use the label_id from the URL parameter directly
        label_to_unassign = NotificationLabel.objects.get(pk=label_id, user=request.user)

        # Check if the label is actually assigned to this notification
        if label_to_unassign in notification.labels.all():
            notification.labels.remove(label_to_unassign)
            messages.success(request, f"Label '{label_to_unassign.name}' removed from notification.")
        else:
            messages.info(request, f"Label '{label_to_unassign.name}' was not assigned to this notification.")

    except NotificationLabel.DoesNotExist:
        messages.error(request, "Label not found or does not belong to you.")
    except Exception as e:  # Catch any other potential errors
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect(reverse("users:notifications-by-label", kwargs={"label_id": label_id}))


@login_required
def recommendation_preferences(request, pk):
    """
    Allow users to customize their game recommendation preferences.

    Args:
        request (HttpRequest)
        pk (int): The primary key of the user

    Returns:
        HttpResponse: Rendered template with recommendation preferences
    """

    if pk != request.user.pk:
        messages.error(request, "You can only manage your own preferences")
        return redirect(reverse("users:user-profile", kwargs={"pk": request.user.pk}))

    from .models import RecommendationPreferences

    preferences = RecommendationPreferences.get_or_create_preferences(request.user)

    if request.method == "POST":
        try:
            preferences.category_weight = min(100, max(0, int(request.POST.get("category_weight", 40))))
            preferences.mechanics_weight = min(100, max(0, int(request.POST.get("mechanics_weight", 30))))
            preferences.designers_weight = min(100, max(0, int(request.POST.get("designers_weight", 15))))
            preferences.complexity_weight = min(100, max(0, int(request.POST.get("complexity_weight", 10))))
            preferences.playtime_weight = min(100, max(0, int(request.POST.get("playtime_weight", 5))))
            preferences.save()
            messages.success(request, "Your recommendation preferences have been updated")
        except ValueError:
            messages.error(request, "Invalid preference values. Please enter numbers between 0 and 100.")

    context = {"preferences": preferences, "user_id": pk}

    return render(request, "users/recommendation_preferences.html", context)


class GroupListView(SingleTableView):
    model = Group
    table_class = GroupTable
    template_name = "users/group_list.html"


class GroupDetailView(DetailView):
    model = Group
    template_name = "users/group_detail.html"


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ["name", "description", "members"]
    template_name = "users/group_create.html"
    success_url = reverse_lazy("group-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        self.object.members.add(self.request.user)

        selected_members = form.cleaned_data["members"]
        for user in selected_members:
            if user != self.request.user:
                GroupInvitation.objects.get_or_create(
                    friend_group=self.object,
                    sender=self.request.user,
                    receiver=user,
                    defaults={"accepted": False, "is_deleted": False},
                )

        return response


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = "users/group_confirm_delete.html"
    success_url = reverse_lazy("group-list")

    def get_queryset(self):
        return Group.objects.filter(created_by=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class GroupJoinView(LoginRequiredMixin, View):
    template_name = "users/group_join.html"

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=kwargs["pk"])
        if request.user in group.members.all():
            messages.error(request, "You are already a member of this group.")
            return redirect(reverse("users:group-detail", kwargs={"pk": group.pk}))
        return render(request, self.template_name, {"group": group})

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=kwargs["pk"])
        if request.user in group.members.all():
            messages.error(request, "You are already a member of this group.")
        else:
            group.members.add(request.user)
            messages.success(request, "You have successfully joined the group.")
        return redirect(reverse("users:group-detail", kwargs={"pk": group.pk}))


class GroupLeaveView(LoginRequiredMixin, View):
    template_name = "users/group_leave.html"

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=kwargs["pk"])
        if request.user not in group.members.all():
            messages.error(request, "You are not a member of this group.")
            return redirect(reverse("users:group-detail", kwargs={"pk": group.pk}))
        return render(request, self.template_name, {"group": group})

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=kwargs["pk"])
        if request.user not in group.members.all():
            messages.error(request, "You are not a member of this group.")
        else:
            group.members.remove(request.user)
            messages.success(request, "You have successfully left the group.")
        return redirect(reverse("users:group-detail", kwargs={"pk": group.pk}))


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "description", "members"]
        widgets = {
            "members": forms.CheckboxSelectMultiple(),
        }


class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "users/group_update.html"

    def get_success_url(self):
        return reverse("users:group-detail", kwargs={"pk": self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        group = self.get_object()
        if request.user not in group.members.all():
            messages.error(request, "You do not have permission to edit this group.")
            return redirect(reverse("users:group-detail", kwargs={"pk": group.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user != self.get_object().created_by:
            form.fields.pop("name", None)
            form.fields.pop("description", None)
        return form
