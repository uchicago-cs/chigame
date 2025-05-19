import pytest

from chigame.achievements.models import Achievement

from .factories import AchievementFactory, MatchFactory


@pytest.mark.django_db
def test_game_users():
    """Test that creating a match adds users to the game"""
    match = MatchFactory.create()
    assert len(match.game.users.all()) == len(match.players.all())
    for player in match.players.all():
        assert player in match.game.users.all()


@pytest.mark.django_db
def test_get_achievement():
    achievement = AchievementFactory.create()
    game = achievement.game
    assert Achievement.get_achievement(name=achievement.name, game=game) == achievement
