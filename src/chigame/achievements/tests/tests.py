from datetime import timedelta

import pytest
from django.utils import timezone

from chigame.achievements.models import UserAchievement
from chigame.achievements.views import get_recent_achievements

from .factories import AchievementFactory, MatchFactory, UserAchievementFactory, UserFactory


@pytest.mark.django_db
def test_game_users():
    """Test that creating a match adds users to the game"""
    match = MatchFactory.create()
    assert len(match.game.users.all()) == len(match.players.all())
    for player in match.players.all():
        assert player in match.game.users.all()


@pytest.mark.django_db
def test_achievement_advance():
    """Test that advancing an achievement works correctly"""
    for _ in range(5):
        achievement = AchievementFactory.create()
        user = UserFactory.create()

        # Advance the achievement for the user
        achievement.advance(user)

        # Check if the user's achievement progress is updated
        user_achievement = UserAchievement.objects.get(user=user, achievement=achievement)
        assert user_achievement.progress == 1
        if 1e-8 > abs(achievement.threshold - 1):
            assert user_achievement.date_earned is None
        else:
            assert user_achievement.date_earned is None


@pytest.mark.django_db
def test_achievement_set_progress():
    achievement = AchievementFactory(threshold=2.0)
    user = UserFactory()

    achievement.set_progress(user, 1.0)
    user_achievement = UserAchievement.objects.get(user=user, achievement=achievement)
    assert abs(user_achievement.progress - 1.0) <= 1e-8

    achievement.set_progress(user, 2.0)
    user_achievement.refresh_from_db()
    assert abs(user_achievement.progress - 2.0) <= 1e-8
    assert user_achievement.date_earned is not None
    assert user_achievement.date_earned == user_achievement.last_updated

    achievement.set_progress(user, 1.0)
    user_achievement.refresh_from_db()
    assert abs(user_achievement.progress - 2.0) <= 1e-8
    assert user_achievement.date_earned is not None
    assert user_achievement.date_earned == user_achievement.last_updated

    achievement.set_progress(user, 1.0, override=True)
    user_achievement.refresh_from_db()
    assert abs(user_achievement.progress - 1.0) <= 1e-8
    assert user_achievement.date_earned is None


@pytest.mark.django_db
def test_get_recent_achievements():
    user = UserFactory()
    # Create 6 achievements with different dates
    for i in range(6):
        UserAchievementFactory(user=user, date_earned=timezone.now() - timedelta(days=i))

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
        UserAchievementFactory(user=user, date_earned=timezone.now() - timedelta(days=i))

    recent = get_recent_achievements(user.id)

    assert len(recent) == 3
    assert all(isinstance(ua, UserAchievement) for ua in recent)
    # Check they are ordered by most recent
    assert recent[0].date_earned > recent[len(recent) - 1].date_earned
