import django_tables2 as tables

from .models import User, UserProfile


class FriendsTable(tables.Table):
    name = tables.Column(verbose_name="Friend's Name")

    class Meta:
        model = UserProfile  # Referencing the UserProfile model
        template_name = "django_tables2/bootstrap.html"
        fields = [""]  # Adjust fields to show relevant information from the UserProfile model


class UserTable(tables.Table):
    name = tables.Column(verbose_name="Name")

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["name", "email"]

        # Add information about top ranking users, total points collected, etc.
