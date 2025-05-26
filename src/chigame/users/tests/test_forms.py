"""
Module for all Form Tests.
"""

import pytest
from django.forms import EmailField
from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _
from faker import Faker

from chigame.users.forms import UserAdminChangeForm, UserAdminCreationForm, UserSignupForm, generate_unique_username
from chigame.users.models import User
from chigame.users.tests.factories import UserFactory

faker = Faker()


class TestUserAdminCreationForm:
    """
    Test class for all tests related to the UserAdminCreationForm
    """

    def test_username_validation_error_msg(self, user: User):
        """
        Tests UserAdminCreation Form's unique validator functions correctly by testing:
            1) A new user with an existing username cannot be added.
            2) Only 1 error is raised by the UserCreation Form
            3) The desired error message is raised
        """

        email = faker.unqiue.email()
        password = faker.password(length=12)

        UserFactory(email=email)

        form = UserAdminCreationForm(
            {
                "email": email,
                "password1": password,
                "password2": password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors
        assert form.errors["email"][0] == _("This email has already been taken.")

    @pytest.mark.django_db
    def test_valid_creation_form(self):
        """
        Tests that the form is valid when email and matching passwords are provided.
        """
        fake_email = faker.unique.email()
        fake_password = faker.password(length=12)
        form = UserAdminCreationForm(
            {
                "email": fake_email,
                "password1": fake_password,
                "password2": fake_password,
            }
        )
        assert form.is_valid()


class TestUserAdminChangeForm:
    def test_email_field_present(self):
        """
        Ensure the admin change form includes the email field and it's of the right type.
        """
        form = UserAdminChangeForm()
        assert "email" in form.fields
        assert isinstance(form.fields["email"], EmailField)


class TestUserSignupForm:
    @pytest.mark.django_db
    def test_auto_username_is_generated(self):
        """
        Ensure that a unique username is automatically generated during signup.
        """
        fake_email = faker.unique.email()
        fake_password = faker.password(length=12)
        form = UserSignupForm()
        form.cleaned_data = {
            "email": fake_email,
            "password1": fake_password,
            "password2": fake_password,
        }
        request = RequestFactory().post("accounts/signup/")
        request.session = {}
        request.user = None

        user = form.save(request)
        assert user.username is not None
        assert len(user.username) >= 4


@pytest.mark.django_db
def test_generate_unique_username_does_not_duplicate_existing():
    """
    Ensure generate_unique_username never returns a username that already exists.
    """
    existing_usernames = set()
    for x in range(50):
        user = UserFactory()
        existing_usernames.add(user.username)

    for y in range(10):
        new_username = generate_unique_username()
        assert new_username not in existing_usernames
        UserFactory(username=new_username)
        existing_usernames.add(new_username)
