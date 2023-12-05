import django_tables2 as tables

from .models import User


class FriendsTable(tables.Table):
    email = tables.Column(
        verbose_name="Email",
        accessor="email",  # Access display_name through the User relationship
        linkify=("users:user-profile", {"pk": tables.A("pk")}),
    )

    class Meta:
        model = User  # Referencing the UserProfile model
        template_name = "django_tables2/bootstrap.html"
        fields = ["email"]  # Adjust fields to show relevant information from the UserProfile model


class UserTable(tables.Table):
    name = tables.Column(verbose_name="Name")

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["name", "first_name", "last_name", "email"]

        # Add information about top ranking users, total points collected, etc.
