import pytest

from .factories import MatchFactory


@pytest.mark.django_db
def test_game_users():
    """Test that creating a match adds users to the game"""
    match = MatchFactory.create()
    assert len(match.game.users.all()) == len(match.players.all())
    for player in match.players.all():
        assert player in match.game.users.all()
