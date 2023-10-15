import django.db.models as models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from chigame.users.managers import UserManager


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
    username = None  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


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


class FriendInvitation(models.Model):
    """
    An invitation from a User to another User, requesting that they become friends.
    """

    sender = models.ForeignKey(User, related_name="sent_friend_invitations", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_friend_invitations", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class FriendGroup(models.Model):
    """
    A group of friends.
    """

    name = models.TextField()
    members = models.ManyToManyField(User)
    created_by = models.ForeignKey(User, related_name="created_groups", on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)


class FriendGroupInvitation(models.Model):
    """
    An invitation to join a group of friends
    """

    friend_group = models.ForeignKey(FriendGroup, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_group_invitations", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_group_invitations", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
