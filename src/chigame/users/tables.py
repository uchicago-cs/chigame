import django_tables2 as tables
from django.utils.html import format_html

from .models import User


class FriendsTable(tables.Table):
    email = tables.Column(
        verbose_name="Email",
        accessor="email",  # Access display_name through the User relationship
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
        model = User  # Referencing the UserProfile model
        template_name = "django_tables2/bootstrap.html"
        fields = [
            "email",
            "online_status",
            "last_seen",
        ]  # Adjust fields to show relevant information from the UserProfile model


class UserTable(tables.Table):
    name = tables.Column(verbose_name="Name")

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["name", "first_name", "last_name", "email"]

        # Add information about top ranking users, total points collected, etc.
