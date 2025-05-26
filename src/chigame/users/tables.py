import django_tables2 as tables
from django.utils.html import format_html

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

    online_status = tables.Column(
        verbose_name="Status",
        accessor="get_online_status",
        orderable=False,
    )

    last_seen = tables.Column(
        verbose_name="Last Seen",
        accessor="get_last_seen_display",
        orderable=False,
    )

    def render_online_status(self, value):
        if value == "online":
            return format_html('<span class="badge bg-success">Online</span>')
        elif value == "recently_active":
            return format_html('<span class="badge bg-warning">Recently Active</span>')
        else:
            return format_html('<span class="badge bg-secondary">Offline</span>')

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = [
            "email",
            "online_status",
            "last_seen",
            "username"
        ]  # Adjust fields to show relevant information from the UserProfile model

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


class GroupTable(tables.Table):
    name = tables.Column(verbose_name="Name")

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["name", "description", "members", "created_by", "date_created"]
