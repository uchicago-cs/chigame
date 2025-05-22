from datetime import timedelta

import pytest
from django.utils import timezone

from chigame.achievements.models import UserAchievement
from chigame.achievements.views import get_recent_achievements

from .factories import CompletedUserAchievementFactory, MatchFactory, UserFactory


@pytest.mark.django_db
def test_game_users():
    """Test that creating a match adds users to the game"""
    match = MatchFactory.create()
    assert len(match.game.users.all()) == len(match.players.all())
    for player in match.players.all():
        assert player in match.game.users.all()


@pytest.mark.django_db
def test_get_recent_achievements():
    user = UserFactory()
    # Create 6 achievements with different dates
    for i in range(6):
        CompletedUserAchievementFactory(user=user, date_earned=timezone.now() - timedelta(days=i))

    recent = get_recent_achievements(user.id)

    assert len(recent) == 5
    assert all(isinstance(ua, UserAchievement) for ua in recent)
    # Check they are ordered by most recent
    assert recent[0].date_earned > recent[len(recent) - 1].date_earned


@pytest.mark.django_db
def test_get_recent_achievements_none():
    user = UserFactory()
    # No achievements created for this user
    recent = get_recent_achievements(user.id)

    assert len(recent) == 0


@pytest.mark.django_db
def test_get_recent_achievements_3():
    user = UserFactory()
    # Create 3 achievements with different dates
    for i in range(3):
        CompletedUserAchievementFactory(user=user, date_earned=timezone.now() - timedelta(days=i))

    recent = get_recent_achievements(user.id)

    assert len(recent) == 3
    assert all(isinstance(ua, UserAchievement) for ua in recent)
    # Check they are ordered by most recent
    assert recent[0].date_earned > recent[len(recent) - 1].date_earned
