"""
Module for all Form Tests.
"""
import pytest

from chigame.users.forms import UserAdminChangeForm, UserAdminCreationForm, UserProfileForm
from chigame.users.models import User, UserProfile

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


class TestUserAdminCreationForm:
    """
    Test class for UserAdminCreationForm
    """

    def test_email_validation_error_msg(self, user: User):
        """
        Tests UserAdminCreationForm's unique email validation error message
        """
        form = UserAdminCreationForm(
            {
                "email": user.email,
                "password1": "My_R@ndom-P@ssw0rd",
                "password2": "My_R@ndom-P@ssw0rd",
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors
        assert form.errors["email"][0] == "This email has already been taken."


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
