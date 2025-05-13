import pytest

from chigame.leaderboards.models import LeaderboardPrivacySetting
from chigame.leaderboards.tests.factories import (
    GameFactory,
    GamePrivacySettingFactory,
    GlobalPrivacySettingFactory,
    LeaderboardFactory,
    LeaderboardSpecificPrivacySettingFactory,
    UserProfileFactory,
)

# ========== TESTS FOR LEADERBOARD PRIVACY SETTING (LPS) ==========
# Hierarchy of privacy settings:
#   1. Specific leaderboard Setting (highest priority)
#   2. Game-level setting
#   3. Global setting (lowest priority)


@pytest.mark.django_db
def test_LPS_get_user_setting_specific_leaderboard():
    """
    Testing that the method get_user_setting returns the correct setting
    when a specific leaderboard is provided.
    If all game and leaderboard are provided, the specific leaderboard setting
    should be returned.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    specific_setting = LeaderboardSpecificPrivacySettingFactory(
        user=user, game=game, leaderboard=leaderboard, complete_opt_out=True, display_as_anonymous=False
    )
    GamePrivacySettingFactory(user=user, game=game, complete_opt_out=False, display_as_anonymous=False)
    GlobalPrivacySettingFactory(user=user, complete_opt_out=False, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == specific_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_game_level():
    """
    Testing that the method get_user_setting returns the correct setting
    when a game is provided.
    If only the game is provided, the setting for it should be returned.
    """
    user = UserProfileFactory()
    game = GameFactory()
    LeaderboardFactory(game=game)
    game_setting = GamePrivacySettingFactory(user=user, game=game, complete_opt_out=True, display_as_anonymous=False)
    GlobalPrivacySettingFactory(user=user, complete_opt_out=False, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game)

    assert test_setting == game_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_global():
    """
    Testing that the method get_user_setting returns the correct setting
    when neither a game nor a leaderboard are provided.
    It should return the global setting.
    """
    user = UserProfileFactory()
    game = GameFactory()
    LeaderboardFactory(game=game)
    global_setting = GlobalPrivacySettingFactory(user=user, complete_opt_out=True, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user)

    assert test_setting == global_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_fallback_to_game_leaderboard_missing():
    """
    Testing that even if a leaderboard is provided, but there is no specific
    setting for it, the method get_user_setting will fall back to the
    game-level setting.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    game_setting = GamePrivacySettingFactory(user=user, game=game, complete_opt_out=True, display_as_anonymous=False)
    GlobalPrivacySettingFactory(user=user, complete_opt_out=False, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == game_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_fallback_to_global_game_missing():
    """
    Testing that even if a leaderboard and game are provided, but there is no specific
    setting for it, the method get_user_setting will fall back to the
    global-level setting.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    global_setting = GlobalPrivacySettingFactory(user=user, complete_opt_out=True, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == global_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


@pytest.mark.django_db
def test_LPS_get_user_setting_none():
    """
    What happens when no settings are created for the user?
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    assert LeaderboardPrivacySetting.get_user_setting(user) is None
    assert LeaderboardPrivacySetting.get_user_setting(user, game) is None
    assert LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard) is None


# ===========================================================
