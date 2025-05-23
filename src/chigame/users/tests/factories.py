from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from factory import Faker, LazyAttribute, SubFactory, post_generation
from factory.django import DjangoModelFactory

from chigame.users.models import FriendInvitation, Group, GroupInvitation, Notification, UserProfile


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


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = SubFactory(UserFactory)
    bio = Faker("sentence", nb_words=35)
    date_joined = Faker("date_time_this_year")


class FriendInvitationFactory(DjangoModelFactory):
    class Meta:
        model = FriendInvitation

    sender = SubFactory(UserFactory)
    receiver = SubFactory(UserFactory)
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
            Notification.MATCH_INVITATION,
            Notification.GROUP_INVITATION,
            Notification.ACHIEVEMENT,
            Notification.TOURNAMENT_INVITATION,
            Notification.TOURNAMENT_INVITATION_ACCEPTED,
            Notification.TOURNAMENT_STARTING,
            Notification.TOURNAMENT_ROUND_COMPLETED,
            Notification.TOURNAMENT_COMPLETED,
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


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    name = Faker("word")
    description = Faker("sentence", nb_words=15)
    created_by = SubFactory(UserFactory)
    date_created = Faker("date_time_this_year")

    @post_generation
    def members(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        self.members.add(*extracted)


class GroupInvitationFactory(DjangoModelFactory):
    class Meta:
        model = GroupInvitation

    friend_group = SubFactory(GroupFactory)
    sender = SubFactory(UserFactory)
    receiver = SubFactory(UserFactory)
    accepted = Faker("boolean")
    timestamp = Faker("date_time_this_year")
    # is_deleted is not set by default because only one active invitation
    # is allowed between sender and receiver
