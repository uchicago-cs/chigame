import random

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

POKEMON_NAMES = [
    "pikachu",
    "bulbasaur",
    "charmander",
    "squirtle",
    "eevee",
    "snorlax",
    "jigglypuff",
    "psyduck",
    "gengar",
    "meowth",
    "charizard",
    "wartortle",
    "ivysaur",
    "venusaur",
    "blastoise",
    "venomoth",
    "venonat",
]

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """

    def save(self, request):
        user = super().save(request)
        user.username = generate_unique_username()
        user.save()
        return user


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


def generate_unique_username():
    """Generates a unique default username for user for signup process.
    Users can change their username after signup in their profile account
    page.
    """
    while True:
        name = random.choice(POKEMON_NAMES)
        number = random.randint(100, 9999)
        username = f"{name}{number}"
        if not User.objects.filter(username=username).exists():
            return username


class FriendInvitationForm(forms.Form):
    """
    Form for sending friend invitations with optional personal messages.
    """

    message = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Let them know why you'd like to be friends! (Gaming buddies, shared interests, etc.)",
                "class": "form-control",
            }
        ),
    )
