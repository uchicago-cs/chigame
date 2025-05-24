import pytest
from django.core.exceptions import ValidationError

from chigame.api.tests.factories import GameFactory
from chigame.games.models import GameList
from chigame.users.models import FriendInvitation, Notification, User, UserProfile

from .factories import (
    FriendInvitationFactory,
    FriendInvitationNotificationFactory,
    GroupFactory,
    GroupInvitationFactory,
    UserFactory,
)


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.pk}/"


@pytest.mark.django_db
def test_create_user_with_email_only():
    # test that user can be created without username, just email
    user = User.objects.create_user(email="test@example.com", password="testpass")
    assert user.email == "test@example.com"
    assert user.username is None


@pytest.mark.django_db
def test_validate_username():
    # test that username cannot be completely numeric
    user = User.objects.create_user(email="test@test.com", username="validname", password="test")
    user.username = "123456"
    with pytest.raises(ValidationError):
        user.full_clean()
        user.save()


@pytest.mark.django_db
def test_profile_creation():
    # start with fresh user without profile and then create profile
    user = UserFactory()
    UserProfile.get_or_create_profile(user)
    assert UserProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_one_active_one_deleted_invitation():
    # Test there can be one active invitation and one deleted invitation
    # There should be no uniqueness constraints on sender and receiver since
    # there can be multiple deleted invitations!
    sender = UserFactory()
    receiver = UserFactory()

    # Create a active invitation, delete it, then create a new one
    old_invitation = FriendInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)
    old_invitation.is_deleted = True
    old_invitation.save()

    # Now create a new active invitation
    new_invitation = FriendInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)

    assert new_invitation.sender == sender
    assert new_invitation.receiver == receiver

    # Only one active invitation
    active_invitations = FriendInvitation.objects.filter(sender=sender, receiver=receiver, is_deleted=False)
    assert active_invitations.count() == 1


@pytest.mark.django_db
def test_friendinvitation_accept_invitation():
    # Test that after accepting invitation, sender and receiver become friends
    sender = UserFactory()
    receiver = UserFactory()
    invitation = FriendInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)
    invitation.accept_invitation()
    assert invitation.accepted is True
    assert sender.friends.filter(pk=receiver.pk).exists()
    assert receiver.friends.filter(pk=sender.pk).exists()


@pytest.mark.django_db
def test_friendinvitation_delete_invitation():
    # Test that after deleting invitation, sender and receiver are not friends
    # Also ensure that the invitation is soft deleted
    sender = UserFactory()
    receiver = UserFactory()
    invitation = FriendInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)
    invitation.delete()
    assert invitation.is_deleted is True
    assert not sender.friends.filter(pk=receiver.pk).exists()
    assert not receiver.friends.filter(pk=sender.pk).exists()


@pytest.mark.django_db
def test_groupinvitation_accept_invitation():
    # Test that after accepting group invitation, receiver is added to group
    sender = UserFactory()
    receiver = UserFactory()
    group = GroupFactory(created_by=sender)
    invitation = GroupInvitationFactory(friend_group=group, sender=sender, receiver=receiver, is_deleted=False)
    invitation.accept_invitation()
    assert invitation.accepted is True
    assert group.members.filter(pk=receiver.pk).exists()


@pytest.mark.django_db
def test_groupinvitation_delete_invitation():
    # Test that after deleting invitation, receiver is not in group
    sender = UserFactory()
    receiver = UserFactory()
    group = GroupFactory(created_by=sender)
    invitation = GroupInvitationFactory(sender=sender, receiver=receiver, is_deleted=False)
    invitation.delete()
    assert invitation.is_deleted is True
    assert not group.members.filter(pk=receiver.pk).exists()


@pytest.mark.django_db
def test_friendinvitation_notification_attrs():
    notification = FriendInvitationNotificationFactory.create()
    assert notification.read is False
    assert notification.visible is True
    assert (
        not notification.first_sent > notification.last_sent
    )  # not comparing equality because last_sent is created after first_sent
    # and they will be different by just a little bit
    notification.renew_notification()
    assert notification.first_sent < notification.last_sent


@pytest.mark.django_db
def test_friendinvitation_notification_mark_x_methods():
    notification = FriendInvitationNotificationFactory.create()

    notification.mark_as_read()
    assert notification.read is True

    notification.mark_as_unread()
    assert notification.read is False

    notification.mark_as_deleted()
    assert notification.visible is False


@pytest.mark.django_db
def test_notificationqueryset_filter_by_receiver():
    user1 = UserFactory()
    user2 = UserFactory()
    user3 = UserFactory()
    FriendInvitationNotificationFactory.create_batch(5, receiver=user1)
    FriendInvitationNotificationFactory.create_batch(4, receiver=user2)
    assert len(Notification.objects.filter_by_receiver(user1)) == 5
    assert len(Notification.objects.filter_by_receiver(user2)) == 4
    assert len(Notification.objects.filter_by_receiver(user3)) == 0


@pytest.mark.django_db
def test_notificationqueryset_filter_by_actor():
    friendinvitation1 = FriendInvitationFactory()
    friendinvitation2 = FriendInvitationFactory()
    friendinvitation3 = FriendInvitationFactory()

    FriendInvitationNotificationFactory.create_batch(5, actor=friendinvitation1)
    FriendInvitationNotificationFactory.create_batch(4, actor=friendinvitation2)

    assert len(Notification.objects.filter_by_actor(friendinvitation1)) == 5
    assert len(Notification.objects.filter_by_actor(friendinvitation2)) == 4
    assert len(Notification.objects.filter_by_actor(friendinvitation3)) == 0


@pytest.mark.django_db
def test_notificationqueryset_get_by_actor():
    friendinvitation1 = FriendInvitationFactory()
    friendinvitation2 = FriendInvitationFactory()
    friendinvitation3 = FriendInvitationFactory()

    FriendInvitationNotificationFactory.create_batch(5, actor=friendinvitation1)
    FriendInvitationNotificationFactory.create_batch(1, actor=friendinvitation2)

    with pytest.raises(Exception):
        Notification.objects.get_by_actor(friendinvitation1)
        Notification.objects.get_by_actor(friendinvitation3)

    notification = Notification.objects.get_by_actor(friendinvitation2)
    assert notification.actor == friendinvitation2

    notification.delete()
    with pytest.raises(Notification.DoesNotExist):
        Notification.objects.get_by_actor(friendinvitation2)


@pytest.mark.django_db
def test_notificationqueryset_mark_x_methods():
    FriendInvitationNotificationFactory.create_batch(5)
    notifications = Notification.objects.all()

    notifications.mark_all_read()
    for notification in notifications:
        assert notification.read is True

    notifications.mark_all_unread()
    for notification in notifications:
        assert notification.read is False

    notifications.mark_all_deleted()
    for notification in notifications:
        assert notification.visible is False


@pytest.mark.django_db
def test_notificationqueryset_is_x_methods():
    FriendInvitationNotificationFactory.create_batch(5)
    notifications = Notification.objects.all()

    assert len(Notification.objects.is_unread()) == 5
    assert len(Notification.objects.is_read()) == 0
    assert len(Notification.objects.is_deleted()) == 0
    assert len(Notification.objects.is_not_deleted()) == 5

    notifications.mark_all_read()
    assert len(Notification.objects.is_unread()) == 0
    assert len(Notification.objects.is_read()) == 5

    notifications.mark_all_deleted()
    assert len(Notification.objects.is_deleted()) == 5
    assert len(Notification.objects.is_not_deleted()) == 0

    notifications.restore_all_deleted()
    assert len(Notification.objects.is_deleted()) == 0
    assert len(Notification.objects.is_not_deleted()) == 5


@pytest.mark.django_db
def test_user_favorites_list_creation():
    # Test that a favorites GameList is automatically created for a user
    user = UserFactory()
    # The signal should have already created the Favorites list
    favorites_list = GameList.objects.get(created_by=user, name="Favorites")
    assert favorites_list.created_by == user
    assert favorites_list.name == "Favorites"


@pytest.mark.django_db
def test_add_game_to_favorites():
    # Test adding a game to user's favorites list
    user = UserFactory()
    game = GameFactory(name="Chess")
    # Get the automatically created favorites list
    favorites_list = GameList.objects.get(created_by=user, name="Favorites")
    favorites_list.games.add(game)

    assert game in favorites_list.games.all()
    assert favorites_list.games.count() == 1


@pytest.mark.django_db
def test_remove_game_from_favorites():
    # Test removing a game from user's favorites list
    user = UserFactory()
    game = GameFactory(name="Monopoly")
    favorites_list = GameList.objects.get(created_by=user, name="Favorites")
    favorites_list.games.add(game)
    assert favorites_list.games.count() == 1

    favorites_list.games.remove(game)
    assert game not in favorites_list.games.all()
    assert favorites_list.games.count() == 0
