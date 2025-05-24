import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from chigame.games.models import Game, GameList
from chigame.users.forms import UserAdminChangeForm
from chigame.users.models import User
from chigame.users.tests.factories import UserFactory
from chigame.users.views import NameUpdateView, UsernameUpdateView, UserRedirectView, user_detail_view, user_list

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest):
        return None

    def test_get_success_url(self, user: User, rf: RequestFactory):
        name_update_view = NameUpdateView()
        username_update_view = UsernameUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        name_update_view.request = request
        username_update_view.request = request
        assert name_update_view.get_success_url() == f"/users/{user.pk}/"
        assert username_update_view.get_success_url() == f"/users/{user.pk}/"

    def test_get_object(self, user: User, rf: RequestFactory):
        name_update_view = NameUpdateView()
        username_update_view = UsernameUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        name_update_view.request = request
        username_update_view.request = request

        assert name_update_view.get_object() == user
        assert username_update_view.get_object() == user

    def test_name_form_valid(self, user: User, rf: RequestFactory):
        name_update_view = NameUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        name_update_view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        name_update_view.form_valid(form)
        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]

    def test_username_form_valid(self, user: User, rf: RequestFactory):
        username_update_view = UsernameUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        username_update_view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        username_update_view.form_valid(form)
        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request
        assert view.get_redirect_url() == f"/users/{user.pk}/"


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()
        response = user_detail_view(request, pk=user.pk)

        assert response.status_code == 200

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, pk=user.pk)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302
        assert response.url == f"{login_url}?next=/fake-url/"


@pytest.mark.django_db
def test_admin_user_list_view(client, rf: RequestFactory):
    request = rf.get("user-list")

    request.user = User.objects.create_user(is_staff=True, name="testuser", password="testpass", email="test@pass.com")
    client.login(email="test@pass.com", password="testpass")

    response = user_list(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_nonadmin_user_list_view(client, rf: RequestFactory):
    request = rf.get("user-list")

    request.user = User.objects.create_user(name="testuser", password="testpass", email="test@pass.com")
    client.login(email="test@pass.com", password="testpass")

    response = user_list(request)

    assert response.status_code == 404


class TestFavoriteGamesViews:
    """Test cases for favorite games functionality in user profiles."""

    @pytest.fixture
    def game1(self):
        return Game.objects.create(
            name="Chess",
            description="Classic strategy game",
            min_players=2,
            max_players=2,
            complexity=3.0,
            expected_playtime=30,
        )

    @pytest.fixture
    def game2(self):
        return Game.objects.create(
            name="Monopoly",
            description="Property trading game",
            min_players=2,
            max_players=8,
            complexity=2.5,
            expected_playtime=120,
        )

    def test_profile_shows_favorite_games(self, client, user, game1):
        """Test that user profile displays favorite games."""
        client.force_login(user)

        # Add game to favorites
        favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=user)
        favorites_list.games.add(game1)

        response = client.get(reverse("users:user-profile", kwargs={"pk": user.pk}))

        assert response.status_code == 200
        assert game1.name in response.content.decode()

    def test_add_favorite_game(self, client, user, game1):
        """Test adding a game to favorites."""
        client.force_login(user)

        response = client.post(reverse("users:add-favorite-game"), {"game_id": game1.id})

        assert response.status_code == 302
        favorites_list = GameList.objects.get(name="Favorites", created_by=user)
        assert game1 in favorites_list.games.all()

    def test_remove_favorite_game(self, client, user, game1):
        """Test removing a game from favorites."""
        client.force_login(user)

        # add game to favorites
        favorites_list, _ = GameList.objects.get_or_create(name="Favorites", created_by=user)
        favorites_list.games.add(game1)

        # Remove game
        response = client.post(reverse("users:remove-favorite-game", kwargs={"game_id": game1.id}))

        # back to profile
        assert response.status_code == 302
        favorites_list.refresh_from_db()
        assert game1 not in favorites_list.games.all()

    def test_empty_favorites(self, client, user):
        """Test profile when user has no favorites."""
        client.force_login(user)

        response = client.get(reverse("users:user-profile", kwargs={"pk": user.pk}))

        assert response.status_code == 200
        assert "You haven't added any favorite games yet" in response.content.decode()

    def test_add_favorite_requires_login(self, client, game1):
        """Test that adding favorites requires authentication."""
        response = client.post(reverse("users:add-favorite-game"), {"game_id": game1.id})

        assert response.status_code == 302
        assert "/accounts/login/" in response.url
