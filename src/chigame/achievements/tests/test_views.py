from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.timesince import timesince

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


@pytest.mark.django_db
def test_get_recent_achievements_frontend(client):
    user = UserFactory()
    client.force_login(user)

    for i in range(6):
        UserAchievementFactory(
            user=user, achievement=AchievementFactory.create(), date_earned=timezone.now() - timedelta(days=i)
        )

    response = client.get(reverse("user_achievements"))
    assert response.status_code == 200

    assert len(response.context["recent_achievements"]) == 5
    assert all(isinstance(ua, UserAchievement) for ua in response.context["recent_achievements"])

    html = response.content.decode()
    for ua in response.context["recent_achievements"]:
        assert ua.achievement.name in html
        assert ua.achievement.game.name in html
        expected_timesince = timesince(ua.date_earned)
        assert expected_timesince.split(",")[0] in html


@pytest.mark.django_db
def test_get_recent_achievements_frontend_no_achievements(client):
    user = UserFactory()
    client.force_login(user)
    # No achievements created for this user
    response = client.get(reverse("user_achievements"))
    assert response.status_code == 200

    assert len(response.context["recent_achievements"]) == 0
    assert "No recent achievements" in response.content.decode()
