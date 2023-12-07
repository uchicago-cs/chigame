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
    Default custom user model for ChiGame.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"), max_length=255, unique=True, blank=True, null=True, validators=[validate_username]
    )
    tokens = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3)], default=1)

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
    display_name = models.TextField()
    bio = models.TextField(blank=True)
    friends = models.ManyToManyField(User, related_name="friendship", blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create_profile(cls, user: User) -> "UserProfile":
        profile, created = cls.objects.get_or_create(user=user)
        return profile


class FriendInvitationManager(models.Manager):
    def get_by_users(self, user1, user2, **kwargs):
        """Gets a friend invitation given two user, each of which can be a sender
        or a receiver"""
        return self.get(Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1), **kwargs)


class FriendInvitation(models.Model):
    """
    An invitation from a User to another User, requesting that they become friends.
    """

    sender = models.ForeignKey(User, related_name="sent_friend_invitations", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_friend_invitations", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = FriendInvitationManager()

    def accept_invitation(self):
        sender = self.sender
        sender_profile = UserProfile.objects.get(user__pk=sender.pk)
        receiver = self.receiver
        receiver_profile = UserProfile.objects.get(user__pk=receiver.pk)
        sender_profile.friends.add(receiver)
        receiver_profile.friends.add(sender)
        self.accepted = True
        self.save()


class Group(models.Model):
    """
    A group of users.
    """

    name = models.TextField()
    members = models.ManyToManyField(User)
    created_by = models.ForeignKey(User, related_name="created_groups", on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)


class GroupInvitation(models.Model):
    """
    An invitation to join a group
    """

    friend_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_group_invitations", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_group_invitations", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


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
    A notification to user
    """

    FRIEND_REQUEST = 1
    REMINDER = 2
    UPCOMING_MATCH = 3
    MATCH_PROPOSAL = 4
    GROUP_INVITATION = 5

    NOTIFICATION_TYPES = (
        (FRIEND_REQUEST, "FRIEND_REQUEST"),
        (REMINDER, "REMINDER"),
        (UPCOMING_MATCH, "UPCOMING_MATCH"),
        (MATCH_PROPOSAL, "MATCH_PROPOSAL"),
        (GROUP_INVITATION, "GROUP_INVITATION"),
    )

    DEFAULT_MESSAGES = {FRIEND_REQUEST: "You have a friend invitation"}

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
