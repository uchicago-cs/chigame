from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from factory import Faker, LazyAttribute, SubFactory, post_generation
from factory.django import DjangoModelFactory
from models import FriendInvitation, Notification


class UserFactory(DjangoModelFactory):
    email = Faker("email")
    name = Faker("name")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["email"]


def get_different_user(user):
    receiver = user
    while receiver.pk == user.pk:
        receiver = SubFactory(UserFactory)
    return receiver


class FriendInvitationFactory(DjangoModelFactory):
    class Meta:
        model = FriendInvitation

    sender = SubFactory(UserFactory)
    receiver = LazyAttribute(
        lambda: get_different_user("..sender")
    )  # special syntax in https://factoryboy.readthedocs.io/en/latest/reference.html#parameters
    accepted = Faker("boolean")
    timestamp = Faker("date_time_this_year")


class BaseNotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    receiver = SubFactory(UserFactory)
    first_sent = last_sent = Faker("date_time_this_year")
    type = Faker(
        "random_element",
        elements=[
            Notification.FRIEND_REQUEST,
            Notification.REMINDER,
            Notification.UPCOMING_MATCH,
            Notification.MATCH_PROPOSAL,
            Notification.GROUP_INVITATION,
        ],
    )
    read = False
    visible = True
    message = Faker("sentence")


class FriendInvitationNotificationFactory(BaseNotificationFactory):
    class Params:
        actor = SubFactory(FriendInvitationFactory)

    actor = LazyAttribute(lambda x: x.actor)
    actor_content_type = LazyAttribute(lambda x: ContentType.objects.get(model=x.actor._meta.model_name))
    actor_object_id = LazyAttribute(lambda x: x.actor.pk)
