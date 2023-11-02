import django_tables2 as tables
from .models import User, UserProfile

class UserTable(tables.Table):
    name = tables.Column(verbose_name="Name")

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ["name"]

class FriendTable(tables.Table):
    display_name = tables.Column(accessor="user__userprofile__display_name",
                                 verbose_name="Friend's Name")
    bio = tables.Column(accessor="user__userprofile__bio",
                        verbose_name="Friend's Bio")

    class Meta:
        model = UserProfile
        template_name = "django_tables2/bootstrap.html"
