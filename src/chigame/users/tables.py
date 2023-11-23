import django_tables2 as tables

from .models import User


class UserTable(tables.Table):
    name = tables.Column(verbose_name="Name")

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["name", "first_name", "last_name"]

        # Add information about top ranking users, total points collected, etc.
