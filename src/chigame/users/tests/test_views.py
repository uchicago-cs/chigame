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

from chigame.users.forms import UserAdminChangeForm
from chigame.users.models import User
from chigame.users.tests.factories import GameFactory, TournamentFactory, UserFactory
from chigame.users.views import UserRedirectView, UserUpdateView, user_detail_view

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
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request
        assert view.get_success_url() == f"/users/{user.pk}/"

    def test_get_object(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        view.form_valid(form)

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


class TestAdminUserDetailView:
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staffuser", password="password", email="staffuser@example.com", is_staff=True
        )
        games = GameFactory.create_batch(1)
        tournaments = TournamentFactory.create_batch(1)
        assert games != tournaments

    # def test_create_tournament_link_accessible_by_staff(self, client):
    #     # Log in as the staff user
    #     client.login(username='staffuser', password='password', email='staffuser@example.com')

    #     # Get the tournaments page
    #     response = client.get(reverse('tournament-list'))

    #     # Check if the "Create a new tournament" link is present in the response
    #     assert '<a href="{}">Create a new tournament</a>'.format(reverse('tournament-create')) in response

    #     # Check if the status code is 200 (OK)
    #     assert response.status_code == 200

    # def test_admin_user_list_view(self, user: User, rf:RequestFactory, client):
    #     request = rf.get("games/tournaments")
    #     request.user = UserFactory()
    #     user.is_staff = True
    #     response = client.get(reverse("tournament-list"))

    #     self.assertContains(response,
    #     '<a href="{}">Create a new tournament</a>'.format(reverse('tournament-create')))
    #     print(response.content)
    #     assert "tournaments" in response.context
