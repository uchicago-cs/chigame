# Generated by Django 4.2.4 on 2023-11-07 23:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("description", models.TextField()),
                ("min_players", models.PositiveIntegerField()),
                ("max_players", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Lobby",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "match_status",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Lobbied"), (2, "In-Progress"), (3, "Finished")], default=1
                    ),
                ),
                ("name", models.TextField()),
                (
                    "game_mod_status",
                    models.PositiveSmallIntegerField(choices=[(1, "Default Game"), (2, "Modified Game")], default=1),
                ),
                ("min_players", models.PositiveIntegerField()),
                ("max_players", models.PositiveIntegerField()),
                ("time_constraint", models.PositiveIntegerField(default=300)),
                ("lobby_created", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="Match",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ],
        ),
        migrations.CreateModel(
            name="MatchProposal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("proposed_time", models.DateTimeField()),
                ("min_players", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("match", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.match")),
            ],
        ),
    ]