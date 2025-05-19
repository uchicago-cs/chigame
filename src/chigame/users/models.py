import django.db.models as models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from chigame.users.managers import UserManager


def validate_username(value):
    """
    Validate that the username is not all numeric.
    """
    if value.isdigit():
        raise ValidationError(_("Username cannot be all numbers."), code="invalid_username")


class User(AbstractUser):
    """
    Custom user model for ChiGame.

    Extends Django's AbstractUser to:
    - Use email instead of username as the primary login field.
    - Allow optional username and name fields.
    - Enforce username validation (not purely numeric).
    - Support symmetrical friend relationships between users.

    When modifying signup fields, update forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"), max_length=255, unique=True, blank=True, null=True, validators=[validate_username]
    )
    # friends is a symmetrical relationship, so it is a many-to-many field
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)
    tokens = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3)], default=1)

    # a moderator can manage/approve game guides in Knowledge Base
    moderator = models.BooleanField(default=False)

    # a toggle to determine if the user wants profanity filter on
    profanity_filter = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    def save(self, *args, **kwargs):
        if self.tokens > 3:
            self.tokens = 3

        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    User profile.

    We separate the profile from the User model, to allow for users
    that don't need a profile on the website (e.g., API-only users)
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    @classmethod
    def get_or_create_profile(cls, user: User) -> "UserProfile":
        profile, created = cls.objects.get_or_create(user=user)
        return profile


class FriendInvitationManager(models.Manager):
    def get_by_users(self, user1, user2, **kwargs):
        """Gets a friend invitation given two user, which can be a sender
        or a receiver"""
        return (
            self.filter(Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1), **kwargs)
            .order_by("-timestamp")
            .first()
        )


class FriendInvitation(models.Model):
    """
    An invitation from a User to another User, requesting that they become
    friends.
    """

    sender = models.ForeignKey(User, related_name="sent_friend_invitations", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_friend_invitations", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = FriendInvitationManager()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("sender", "receiver")

    def accept_invitation(self):
        """
        Accept a friend invitation.
        """
        sender = self.sender
        receiver = self.receiver
        # add the receiver to the sender's friends list (it is symmetrical)
        sender.friends.add(receiver)
        # set the invitation as accepted
        self.accepted = True
        self.save()

    # override default delete
    def delete(self):
        self.is_deleted = True
        self.save()


class Group(models.Model):
    """
    A group of users.

    Groups are created by a user (creator) and can have multiple members.
    """

    name = models.TextField()
    members = models.ManyToManyField(User)
    created_by = models.ForeignKey(User, related_name="created_groups", on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)


class GroupInvitation(models.Model):
    """
    An invitation to join a group.
    """

    friend_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_group_invitations", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_group_invitations", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def accept_invitation(self):
        """
        Accept a group invitation.
        """
        receiver = self.receiver
        self.friend_group.members.add(receiver)
        self.accepted = True
        self.save()

    def delete(self):
        self.is_deleted = True
        self.save()


class NotificationQuerySet(models.QuerySet):
    def filter_by_actor(self, actor, include_deleted=False, **kwargs):
        try:
            actor_content_type = ContentType.objects.get(model=actor._meta.model_name)
            actor_object_id = actor.pk
            queryset = self.filter(actor_content_type=actor_content_type, actor_object_id=actor_object_id, **kwargs)
            if not include_deleted:
                queryset = queryset.is_not_deleted()
            return queryset

        except ContentType.DoesNotExist:
            raise ValueError(f"The model {actor.label} is not registered in content type")

    def get_by_actor(self, actor, include_deleted=False, **kwargs):
        try:
            actor_content_type = ContentType.objects.get(model=actor._meta.model_name)
            actor_object_id = actor.pk
            notification = self.get(actor_content_type=actor_content_type, actor_object_id=actor_object_id, **kwargs)
            if not include_deleted and not notification.visible:
                raise Notification.DoesNotExist
            return notification

        except ContentType.DoesNotExist:
            raise ValueError(f"The model {actor.label} is not registered in content type")

    def filter_by_receiver(self, receiver, deleted=False):
        queryset = self.filter(receiver=receiver)
        if not deleted:
            queryset = queryset.is_not_deleted()
        else:
            queryset = queryset.is_deleted()
        return queryset

    def filter_by_type(self, type, include_deleted=False):
        if type not in [type[0] for type in Notification.NOTIFICATION_TYPES]:
            raise ValueError(f"{type} is not a valid type")
        queryset = self.filter(type=type)
        if not include_deleted:
            queryset = queryset.is_not_deleted()
        return queryset

    def filter_by_category(self, category, include_deleted=False):
        queryset = self.filter(category=category)
        if not include_deleted:
            queryset = queryset.is_not_deleted()
        return queryset

    def mark_all_unread(self):
        self.update(read=False)

    def mark_all_read(self):
        self.update(read=True)

    def mark_all_deleted(self):
        self.update(visible=False)

    def restore_all_deleted(self):
        self.update(visible=True)

    def is_read(self):
        return self.filter(read=True)

    def is_unread(self):
        return self.filter(read=False)

    def is_deleted(self):
        return self.filter(visible=False)

    def is_not_deleted(self):
        return self.filter(visible=True)


class Notification(models.Model):
    """
    A notification to user.

    Supports different types (friend request, match reminder, etc.).
    Links to an actor object (e.g., another user or a lobby) using a GenericForeignKey.
    Handles visibility, read/unread status, and timestamping of events.
    """

    CATEGORY_CHOICES = [
        ("inbox", "Inbox"),
        ("spam", "Spam"),
        ("social", "Social"),
        ("promotions", "Promotions"),
        ("updates", "Updates"),
        ("archived", "Archived"),
    ]

    FRIEND_REQUEST = 1
    REMINDER = 2
    UPCOMING_MATCH = 3
    MATCH_PROPOSAL = 4
    GROUP_INVITATION = 5
    ACHIEVEMENT = 6

    NOTIFICATION_TYPES = (
        (FRIEND_REQUEST, "FRIEND_REQUEST"),
        (REMINDER, "REMINDER"),
        (UPCOMING_MATCH, "UPCOMING_MATCH"),
        (MATCH_PROPOSAL, "MATCH_PROPOSAL"),
        (GROUP_INVITATION, "GROUP_INVITATION"),
        (ACHIEVEMENT, "ACHIEVEMENT"),
    )

    DEFAULT_MESSAGES = {FRIEND_REQUEST: "You have a friend invitation"}

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="inbox")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    first_sent = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(auto_now_add=True)
    type = models.PositiveIntegerField(choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    actor_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    actor_object_id = models.PositiveIntegerField()
    actor = GenericForeignKey("actor_content_type", "actor_object_id")
    message = models.CharField(max_length=255, blank=True, null=True)
    objects = NotificationQuerySet.as_manager()
    bookmarked = models.BooleanField(default=False)
    labels = models.ManyToManyField("NotificationLabel", blank=True, related_name="notifications")

    class Meta:
        unique_together = ["receiver", "actor_content_type", "actor_object_id", "type"]

    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save()

    def mark_as_unread(self):
        if self.read:
            self.read = False
        if not self.visible:
            self.visible = True
        self.save()

    def mark_as_deleted(self):
        if self.visible:
            self.visible = False
            self.save()

    def renew_notification(self):
        self.last_sent = timezone.now()
        self.save()

    def get_style_key(self):
        # For Mapping integer types to the stringsC SS expects
        type_map = {
            self.FRIEND_REQUEST: "friend",
            self.REMINDER: "system",
            self.UPCOMING_MATCH: "match",
            self.MATCH_PROPOSAL: "match",
            self.GROUP_INVITATION: "group",
            self.ACHIEVEMENT: "achievement",
        }
        return type_map.get(self.type, "default")

    def get_rich_message(self):
        actor = self.actor

        # Default message: Use pre-set message, then type-specific default, then generic default
        default_message_for_type = self.DEFAULT_MESSAGES.get(self.type, "You have a new notification.")
        final_fallback_message = self.message or default_message_for_type

        if not actor:
            return final_fallback_message

        try:
            if self.type == self.FRIEND_REQUEST:
                if hasattr(actor, "sender") and actor.sender:
                    # Try to get username, fallback to name, then to "Someone"
                    sender_name = (
                        getattr(actor.sender, "username", None) or getattr(actor.sender, "name", None) or "Someone"
                    )
                    return f"{sender_name} sent you a friend request."
                return default_message_for_type

            elif self.type == self.GROUP_INVITATION:
                if (
                    hasattr(actor, "sender")
                    and actor.sender
                    and hasattr(actor, "friend_group")
                    and actor.friend_group
                    and hasattr(actor.friend_group, "name")
                ):
                    sender_name = (
                        getattr(actor.sender, "username", None) or getattr(actor.sender, "name", None) or "Someone"
                    )
                    group_name = actor.friend_group.name
                    return f"{sender_name} invited you to join the group '{group_name}'."
                return self.message or "You have a group invitation."

            # For all other notification types, use the existing message or the type-specific default
            return final_fallback_message

        except AttributeError:
            return final_fallback_message  # Safe fallback in case of unexpected errors

    def get_icon_class(self):
        if self.type == self.FRIEND_REQUEST:
            return "bi-person-plus-fill"
        elif self.type == self.GROUP_INVITATION:
            return "bi-people-fill"
        elif self.type == self.UPCOMING_MATCH:
            return "bi-calendar-event-fill"
        elif self.type == self.MATCH_PROPOSAL:
            return "bi-joystick"
        elif self.type == self.ACHIEVEMENT:
            return "bi-star-fill"
        elif self.type == self.REMINDER:
            return "bi-info-circle-fill"
        else:
            return "bi-bell-fill"


class BaseNotificationHandler:
    def __init__(self, notification):
        self.notification = notification

    def get_redirect_str(self):
        raise NotImplementedError("Subclasses must implement get_redirect_str")


# Paths must be updated as urls are added


class FriendRequestNotification(BaseNotificationHandler):
    """
    Handles redirection logic for friend request notifications. Redirects the
    user to the sender's profile page upon interaction.
    """

    def get_redirect_str(self):
        return reverse("users:user-profile", kwargs={"pk": self.notification.actor.sender.pk})


class MatchProposalNotification(BaseNotificationHandler):
    """
    Handles redirection logic for match proposal notifications. Redirects the
    user to the lobby of the match upon interaction.
    """

    def get_redirect_str(self):
        return reverse("games:lobby-details", kwargs={"pk": self.notification.actor.lobby.pk})


class GroupInvitationNotification(BaseNotificationHandler):
    """
    Handles redirection logic for group invitation notifications. Redirects the
    user to the group page upon interaction.
    """

    def get_redirect_str(self):
        raise NotImplementedError("Group invitation notifications do not have a redirect URL")


class ReminderNotification(BaseNotificationHandler):
    """
    Handles redirection logic for reminder notifications. Redirects the
    user to the notification page upon interaction.
    """

    def get_redirect_str(self):
        raise NotImplementedError("Reminder notifications do not have a redirect URL")


class UpcomingMatchNotification(BaseNotificationHandler):
    """
    Handles redirection logic for upcoming match notifications. Redirects the
    user to the lobby of the match upon interaction.
    """

    def get_redirect_str(self):
        return reverse("games:lobby-details", kwargs={"pk": self.notification.actor.lobby.pk})


class NotificationLabel(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_labels")

    class Meta:
        unique_together = ("name", "user")

    def __str__(self):
        return self.name
