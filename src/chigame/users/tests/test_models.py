import pytest

from chigame.users.models import Notification, User

from .factories import FriendInvitationFactory, FriendInvitationNotificationFactory, UserFactory


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.pk}/"


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
