from django.apps import AppConfig
from django.core.management import call_command


class GamesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chigame.games"

    def ready(self):
        # Load the 'mechanics_categories_fixtures.json' fixture
        call_command("loaddata", "mechanics_categories_fixtures", app_label="games")
