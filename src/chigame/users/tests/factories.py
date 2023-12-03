from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from factory import Faker, LazyAttribute, SubFactory, lazy_attribute, post_generation
from factory.django import DjangoModelFactory

from chigame.games.models import Game, Tournament
from chigame.users.models import FriendInvitation, Notification


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


class FriendInvitationFactory(DjangoModelFactory):
    class Meta:
        model = FriendInvitation

    sender = SubFactory(UserFactory)
    accepted = Faker("boolean")
    timestamp = Faker("date_time_this_year")

    @lazy_attribute
    def receiver(self):
        return FriendInvitationFactory.get_different_user(self.sender)

    @staticmethod
    def get_different_user(sender):
        receiver = sender
        while receiver.pk == sender.pk:
            receiver = UserFactory()
        return receiver


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


class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game

    name = Faker("name")
    description = Faker("sentence", nb_words=8)
    min_players = Faker("random_int", min=1, max=10)
    max_players = Faker("random_int", min=11, max=20)
    complexity = Faker("random_int", min=1.1, max=4.9)


class TournamentFactory(DjangoModelFactory):
    class Meta:
        model = Tournament

    name = Faker("name")
    game = SubFactory(GameFactory)
    registration_start_date = Faker("date_time_between", start_date="-1d", end_date="now")
    registration_end_date = Faker("date_time_between", start_date=("registration_start_date"), end_date="+7d")
    tournament_start_date = Faker("date_time_between", start_date=("registration_end_date"), end_date="+14d")
    tournament_end_date = Faker("date_time_between", start_date=("tournament_start_date"), end_date="+30d")
    max_players = Faker("random_int", min=21, max=30)
    description = None
    rules = None
    draw_rules = None
    num_winner = 1
