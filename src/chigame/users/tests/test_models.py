import pytest

from chigame.users.models import User

from .factories import FriendInvitationNotificationFactory


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.pk}/"


@pytest.mark.django_db
def test_friendinvitation_notification_attrs():
    notification = FriendInvitationNotificationFactory.create()
    assert notification.read is False
    assert notification.visible is True
    assert not notification.first_sent > notification.last_sent  # not comparing equality because
    # last_sent is created after first_sent
    # and they will be different by just a little bit
    notification.renew_notification()
    assert notification.first_sent < notification.last_sent


@pytest.mark.django_db
def test_friendinvitation_notification_mark_methods():
    notification = FriendInvitationNotificationFactory.create()

    notification.mark_as_read()
    assert notification.read is True

    notification.mark_as_unread()
    assert notification.read is False

    notification.mark_as_deleted()
    assert notification.visible is False
