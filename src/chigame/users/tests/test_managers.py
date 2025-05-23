from io import StringIO

import pytest
from django.core.management import call_command

from chigame.users.models import FriendInvitation, User

from .factories import FriendInvitationFactory, UserFactory


@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(
            email="john@example.com",
            password="something-r@nd0m!",
        )
        assert user.email == "john@example.com"
        assert not user.is_staff
        assert not user.is_superuser
        assert user.check_password("something-r@nd0m!")
        assert user.username is None

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="something-r@nd0m!",
        )
        assert user.email == "admin@example.com"
        assert user.is_staff
        assert user.is_superuser
        assert user.username is None

    def test_create_superuser_username_ignored(self):
        user = User.objects.create_superuser(
            email="test@example.com",
            password="something-r@nd0m!",
        )
        assert user.username is None


@pytest.mark.django_db
def test_createsuperuser_command():
    """Ensure createsuperuser command works with our custom manager."""
    out = StringIO()
    command_result = call_command(
        "createsuperuser",
        "--email",
        "henry@example.com",
        interactive=False,
        stdout=out,
    )

    assert command_result is None
    assert out.getvalue() == "Superuser created successfully.\n"
    user = User.objects.get(email="henry@example.com")
    assert not user.has_usable_password()


@pytest.mark.django_db
def test_friendinvitation_manager():
    # Test that the manager returns the correct friend invitation between two users
    sender = UserFactory()
    receiver = UserFactory()
    invitation = FriendInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)
    assert FriendInvitation.objects.get_by_users(sender, receiver) == invitation
    assert FriendInvitation.objects.get_by_users(receiver, sender) == invitation


@pytest.mark.django_db
def test_friendinvitation_manager_none():
    # Test that the manager returns None if there is no invitation between the two users
    sender = UserFactory()
    receiver = UserFactory()
    invitation = FriendInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)
    assert FriendInvitation.objects.get_by_users(sender, UserFactory()) is None
    assert FriendInvitation.objects.get_by_users(UserFactory(), receiver) is None
    assert FriendInvitation.objects.get_by_users(sender, receiver) == invitation
    assert FriendInvitation.objects.get_by_users(receiver, sender) == invitation


@pytest.mark.django_db
def test_friendinvitation_manager_multiple():
    # Test that the manager returns the correct invitation if there are multiple invitations
    sender = UserFactory()
    receiver = UserFactory()
    invitation = FriendInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)
    sender2 = UserFactory()
    receiver2 = UserFactory()
    invitation2 = FriendInvitationFactory(sender=sender2, receiver=receiver2, is_deleted=False)
    assert FriendInvitation.objects.get_by_users(sender, receiver) == invitation
    assert FriendInvitation.objects.get_by_users(receiver, sender) == invitation
    assert FriendInvitation.objects.get_by_users(sender2, receiver2) == invitation2
    assert FriendInvitation.objects.get_by_users(receiver2, sender2) == invitation2
