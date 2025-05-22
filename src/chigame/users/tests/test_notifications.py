import pytest
from django.contrib.contenttypes.models import ContentType

from chigame.users.models import Notification, NotificationLabel
from chigame.users.tests.factories import FriendInvitationFactory, FriendInvitationNotificationFactory, UserFactory


@pytest.mark.django_db
def test_notification_default_category_and_label():
    user = UserFactory()
    actor = FriendInvitationFactory()
    content_type = ContentType.objects.get_for_model(actor)

    notif = Notification.objects.create(
        receiver=user,
        type=Notification.FRIEND_REQUEST,
        actor_content_type=content_type,
        actor_object_id=actor.pk,
        message="Friend request received",
    )

    assert notif.category == "inbox"
    assert notif.read is False
    assert notif.visible is True
    assert notif.labels.count() == 0


@pytest.mark.django_db
def test_assign_label_to_notification():
    user = UserFactory()
    label = NotificationLabel.objects.create(user=user, name="Important")
    notif = FriendInvitationNotificationFactory(receiver=user)

    notif.labels.add(label)
    notif.save()

    assert label in notif.labels.all()


@pytest.mark.django_db
def test_label_uniqueness_per_user():
    user = UserFactory()
    NotificationLabel.objects.create(user=user, name="Work")

    with pytest.raises(Exception):
        # supposed to violate uniqueness constraint
        NotificationLabel.objects.create(user=user, name="Work")


@pytest.mark.django_db
def test_notification_label_reverse_lookup():
    user = UserFactory()
    label = NotificationLabel.objects.create(user=user, name="Social")

    notif1 = FriendInvitationNotificationFactory(receiver=user)
    notif2 = FriendInvitationNotificationFactory(receiver=user)
    notif1.labels.add(label)
    notif2.labels.add(label)

    assert set(label.notifications.all()) == {notif1, notif2}


@pytest.mark.django_db
def test_bookmark_toggle():
    notif = FriendInvitationNotificationFactory()
    assert notif.bookmarked is False

    notif.bookmarked = True
    notif.save()

    assert notif.bookmarked is True

    notif.bookmarked = False
    notif.save()

    assert notif.bookmarked is False


@pytest.mark.django_db
def test_mark_as_deleted_soft_deletion():
    notif = FriendInvitationNotificationFactory()
    assert notif.visible is True

    notif.mark_as_deleted()
    assert notif.visible is False
