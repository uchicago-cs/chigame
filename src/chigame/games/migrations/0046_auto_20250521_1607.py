import base64
from django.db import migrations

def insert_twine_game(apps, schema_editor):
    Game = apps.get_model("games", "Game")

    with open("src/chigame/games/migrations/twine_b64.txt", "rb") as f:
        html_bytes = base64.b64decode(f.read())

    Game.objects.create(
        name="Midterm Project",
        description="Uploaded via migration",
        twine_file=html_bytes,
        min_players=1,
        max_players=1
    )

class Migration(migrations.Migration):

    dependencies = [
        ("games", "0045_merge_20250521_1434"),
    ]

    operations = [
        migrations.RunPython(insert_twine_game, atomic=False),
    ]
