import django_tables2 as tables

from .models import User


class FriendsTable(tables.Table):
    """
    Table to display a user's friends in user_friend_list.html
    """

    username = tables.Column(
        verbose_name="",  # Empty string to hide the column header because it's not needed
        accessor="username",
        linkify=("users:user-profile", {"pk": tables.A("pk")}),
    )

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["username"]
        attrs = {
            "class": "table",
            "thead": {
                "class": "d-none"
            },  # This hides the entire header row because it's not needed since it is self-explanatory
        }


class UserTable(tables.Table):
    name = tables.Column(verbose_name="Name")

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["name", "first_name", "last_name", "email"]

        # Add information about top ranking users, total points collected, etc.
