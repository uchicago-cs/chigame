import sys
import os
import base64
from django.db import migrations

def insert_twine_game(apps, schema_editor):
    # Skip during tests or if the file is missing
    if "test" in sys.argv or os.environ.get("CI") == "true":
        return

    Game = apps.get_model("games", "Game")
    file_path = "src/chigame/games/migrations/twine_b64.txt"

    if not os.path.exists(file_path):
        print(f"Skipping migration: file not found at {file_path}")
        return

    with open(file_path, "rb") as f:
        html_bytes = base64.b64decode(f.read())

    Game.objects.create(
        name="Twine Test Game",
        description="Uploaded via migration",
        twine_file=html_bytes,
        min_players=1,
        max_players=1,
        complexity=1,
    )

class Migration(migrations.Migration):

    dependencies = [
        ("games", "0045_merge_20250521_1434"),
    ]

    operations = [
        migrations.RunPython(insert_twine_game, atomic=False),
    ]
