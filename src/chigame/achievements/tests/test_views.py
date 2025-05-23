import json
from datetime import timedelta

import pytest
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from chigame.achievements.models import UserAchievement
from chigame.achievements.views import get_pinned_achievements, get_recent_achievements, toggle_pin_achievement

from .factories import AchievementFactory, GameFactory, MatchFactory, UserAchievementFactory, UserFactory


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
def test_user_achievements_view_own_profile_1(client):
    user = UserFactory()
    client.force_login(user)

    game = GameFactory()
    ach1 = AchievementFactory(game=game, threshold=0)
    ach2 = AchievementFactory(game=game, threshold=10)

    # one unlocked, one partial progress
    UserAchievementFactory(user=user, achievement=ach1, date_earned=timezone.now())
    UserAchievementFactory(user=user, achievement=ach2, progress=5)

    url = reverse("user_achievements")
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["viewing_own_profile"] is True
    assert response.context["user_profile"] == user
    assert "games_with_achievements" in response.context
    assert "overall_stats" in response.context

    overall = response.context["overall_stats"]
    assert overall["unlocked"] == 1
    assert overall["total"] == 2


@pytest.mark.django_db
def test_user_achievements_view_own_profile_2(client):
    user = UserFactory()
    client.force_login(user)

    game = GameFactory()
    ach1 = AchievementFactory(game=game, threshold=0)
    ach2 = AchievementFactory(game=game, threshold=10)

    # both unlocked
    UserAchievementFactory(user=user, achievement=ach1, date_earned=timezone.now())
    UserAchievementFactory(user=user, achievement=ach2, date_earned=timezone.now())

    url = reverse("user_achievements")
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["viewing_own_profile"] is True
    assert response.context["user_profile"] == user
    assert "games_with_achievements" in response.context
    assert "overall_stats" in response.context

    overall = response.context["overall_stats"]
    assert overall["unlocked"] == 2
    assert overall["total"] == 2


@pytest.mark.django_db
def test_user_achievements_view_own_profile_3(client):
    user = UserFactory()
    client.force_login(user)

    url = reverse("user_achievements")
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["viewing_own_profile"] is True
    assert response.context["user_profile"] == user
    assert "games_with_achievements" in response.context
    assert "overall_stats" in response.context

    overall = response.context["overall_stats"]
    assert overall["unlocked"] == 0
    assert overall["total"] == 0


@pytest.mark.django_db
def test_get_pinned_achievements_1():
    user = UserFactory()

    # Create 6 pinned achievements with decreasing dates
    for i in range(6):
        UserAchievementFactory(user=user, date_earned=timezone.now() - timedelta(days=i), pinned=True)

    # Create mock request with the user
    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    response = get_pinned_achievements(request)
    assert response.status_code == 200

    data = json.loads(response.content.decode("utf-8"))
    assert "pinned_achievements" in data
    assert len(data["pinned_achievements"]) == 6
    assert all("id" in ach for ach in data["pinned_achievements"])


@pytest.mark.django_db
def test_get_pinned_achievements_none():
    user = UserFactory()

    # No pinned achievements created for this user
    # Create mock request with the user
    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    response = get_pinned_achievements(request)
    assert response.status_code == 200

    data = json.loads(response.content.decode("utf-8"))
    assert "pinned_achievements" in data
    assert len(data["pinned_achievements"]) == 0


@pytest.mark.django_db
def test_get_pinned_achievements_2():
    user = UserFactory()

    # Create 3 pinned achievements with different dates
    for i in range(3):
        UserAchievementFactory(user=user, date_earned=timezone.now() - timedelta(days=i), pinned=True)

    for i in range(2):
        UserAchievementFactory(user=user, date_earned=timezone.now() - timedelta(days=i), pinned=False)

    # Create mock request with the user
    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    response = get_pinned_achievements(request)
    assert response.status_code == 200

    data = json.loads(response.content.decode("utf-8"))
    assert "pinned_achievements" in data
    assert len(data["pinned_achievements"]) == 3


@pytest.mark.django_db
def test_toggle_pin_achievement():
    user = UserFactory()
    achievement = AchievementFactory()

    factory = RequestFactory()
    request = factory.post("/")
    request.user = user

    response = toggle_pin_achievement(request, achievement.id)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["status"] == "success"
    assert data["pinned"] is True

    assert UserAchievement.objects.filter(user=user, achievement=achievement, pinned=True).exists()


@pytest.mark.django_db
def test_toggle_pin_achievement_existing():
    user = UserFactory()
    achievement = AchievementFactory()
    ua = UserAchievement.objects.create(user=user, achievement=achievement, pinned=True, date_earned=timezone.now())

    factory = RequestFactory()
    request = factory.post("/")
    request.user = user

    response = toggle_pin_achievement(request, achievement.id)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["status"] == "success"
    assert data["pinned"] is False

    ua.refresh_from_db()
    assert ua.pinned is False


@pytest.mark.django_db
def test_toggle_pin_achievement_rejects_non_post():
    user = UserFactory()
    achievement = AchievementFactory()

    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    response = toggle_pin_achievement(request, achievement.id)
    assert response.status_code == 400
    data = json.loads(response.content.decode("utf-8"))
    assert data["status"] == "error"
