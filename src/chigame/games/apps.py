from django.apps import AppConfig
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


class GamesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chigame.games"

    def ready(self):
        """
        The following code installs the mechanics and categories fixtures into the database
        The point of the try/expect is to make sure the database is created beforehand
              This is necessary because `python3 manage.py check` is run before the migrations on the CI
        """
        try:
            # Connection is used to make queries
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM games_mechanic LIMIT 1;")
                call_command("loaddata", "mechanics_categories_fixtures", app_label="games")
        except OperationalError:
            pass
