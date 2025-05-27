"""
Module for all Form Tests.
"""
import pytest
from django.forms import EmailField
from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _
from faker import Faker

from chigame.users.forms import (
    UserAdminChangeForm,
    UserAdminCreationForm,
    UserProfileForm,
    UserSignupForm,
    generate_unique_username,
)
from chigame.users.models import User, UserProfile
from chigame.users.tests.factories import UserFactory

faker = Faker()

pytestmark = pytest.mark.django_db


class TestUserAdminChangeForm:
    """
    Test class for UserAdminChangeForm
    """

    def test_email_validation_error_msg(self, user: User):
        """
        Tests UserAdminChangeForm's unique email validation error message
        """
        form = UserAdminChangeForm(
            {
                "email": user.email,
                "date_joined": "2024-01-01",
                "tokens": 0,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors
        assert form.errors["email"][0] == "User with this Email address already exists."

        email = faker.unique.email()
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
        assert form.errors["email"][0] == "This email has already been taken."

    def test_email_field_present(self):
        """
        Ensure the admin change form includes the email field and it's of the right type.
        """
        form = UserAdminChangeForm()
        assert "email" in form.fields
        assert isinstance(form.fields["email"], EmailField)


class TestUserProfileForm:
    """
    Test class for UserProfileForm
    """

    def test_valid_bio(self, user: User):
        """
        Tests that a valid bio (under 500 characters) is accepted
        """
        profile = UserProfile.objects.create(user=user, bio="")
        form = UserProfileForm({"bio": "This is a valid bio that is under 500 characters."}, instance=profile)

        assert form.is_valid()

    def test_bio_character_limit(self, user: User):
        """
        Tests that bio over 500 characters is rejected
        """
        profile = UserProfile.objects.create(user=user, bio="")
        long_bio = "a" * 501  # 501 characters
        form = UserProfileForm({"bio": long_bio}, instance=profile)

        assert not form.is_valid()
        assert "bio" in form.errors
        assert "Ensure this value has at most 500 characters" in form.errors["bio"][0]

    def test_bio_exactly_500_characters(self, user: User):
        """
        Tests that bio with exactly 500 characters is accepted
        """
        profile = UserProfile.objects.create(user=user, bio="")
        bio_500_chars = "a" * 500  # Exactly 500 characters
        form = UserProfileForm({"bio": bio_500_chars}, instance=profile)

        assert form.is_valid()

    def test_empty_bio(self, user: User):
        """
        Tests that empty bio is valid
        """
        profile = UserProfile.objects.create(user=user, bio="")
        form = UserProfileForm({"bio": ""}, instance=profile)

        assert form.is_valid()
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
