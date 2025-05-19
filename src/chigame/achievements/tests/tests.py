import pytest

from chigame.achievements.models import UserAchievement

from .factories import AchievementFactory, MatchFactory, UserFactory


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
