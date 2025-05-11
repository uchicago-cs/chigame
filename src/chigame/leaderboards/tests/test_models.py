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


def test_LPS_get_user_setting_game_level():
    """
    Testing that the method get_user_setting returns the correct setting
    when a game is provided.
    If only the game is provided, the setting for it should be returned.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    game_setting = GamePrivacySettingFactory(user=user, complete_opt_out=True, display_as_anonymous=False)
    GlobalPrivacySettingFactory(user=user, complete_opt_out=False, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == game_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


def test_LPS_get_user_setting_global():
    """
    Testing that the method get_user_setting returns the correct setting
    when neither a game nor a leaderboard are provided.
    It should return the global setting.
    """
    user = UserProfileFactory()
    game = GameFactory()
    leaderboard = LeaderboardFactory(game=game)
    global_setting = GlobalPrivacySettingFactory(user=user, complete_opt_out=True, display_as_anonymous=False)

    test_setting = LeaderboardPrivacySetting.get_user_setting(user, game, leaderboard)

    assert test_setting == global_setting
    assert test_setting.complete_opt_out
    assert not test_setting.display_as_anonymous


# ===========================================================
