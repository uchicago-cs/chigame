from django.urls import resolve, reverse

from chigame.users.models import User


def test_detail(user: User):
    assert reverse("users:detail", kwargs={"pk": user.pk}) == f"/users/{user.pk}/"
    assert resolve(f"/users/{user.pk}/").view_name == "users:detail"


def test_update():
    assert reverse("users:update-name") == "/users/~update-name/"
    assert resolve("/users/~update-name/").view_name == "users:update-name"
    assert reverse("users:update-username") == "/users/~update-username/"
    assert resolve("/users/~update-username/").view_name == "users:update-username"


def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"


def test_add_favorite_game():
    game_id = 123
    assert reverse("users:add-favorite-game", kwargs={"game_id": game_id}) == f"/users/favorite-games/add/{game_id}/"
    assert resolve(f"/users/favorite-games/add/{game_id}/").view_name == "users:add-favorite-game"


def test_remove_favorite_game():
    game_id = 456
    assert (
        reverse("users:remove-favorite-game", kwargs={"game_id": game_id})
        == f"/users/favorite-games/remove/{game_id}/"
    )
    assert resolve(f"/users/favorite-games/remove/{game_id}/").view_name == "users:remove-favorite-game"
