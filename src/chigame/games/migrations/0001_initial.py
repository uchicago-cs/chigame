# Generated by Django 4.2.4 on 2023-11-13 18:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Chat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ],
        ),
        migrations.CreateModel(
            name="Game",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("description", models.TextField()),
                ("year_published", models.PositiveIntegerField(null=True)),
                ("image", models.URLField(default="/static/images/no_picture_available.png")),
                ("rules", models.TextField(null=True)),
                ("min_players", models.PositiveIntegerField()),
                ("max_players", models.PositiveIntegerField()),
                ("suggested_age", models.PositiveSmallIntegerField(null=True)),
                ("expected_playtime", models.PositiveIntegerField(null=True)),
                ("min_playtime", models.PositiveIntegerField(null=True)),
                ("max_playtime", models.PositiveIntegerField(null=True)),
                ("complexity", models.PositiveSmallIntegerField(null=True)),
                ("BGG_id", models.PositiveIntegerField(null=True)),
                ("category", models.ManyToManyField(related_name="games", to="games.category")),
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
                (
                    "created_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("members", models.ManyToManyField(related_name="lobbies", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Match",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_played", models.DateTimeField()),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("lobby", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="games.lobby")),
            ],
        ),
        migrations.CreateModel(
            name="Mechanic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Tournament",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("max_players", models.PositiveIntegerField()),
                ("description", models.TextField()),
                ("rules", models.TextField()),
                ("draw_rules", models.TextField()),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("matches", models.ManyToManyField(related_name="matches", to="games.match")),
                ("players", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                (
                    "winners",
                    models.ManyToManyField(blank=True, related_name="won_tournaments", to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Publisher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("website", models.URLField(null=True)),
                ("year_established", models.PositiveIntegerField(null=True)),
                ("games", models.ManyToManyField(related_name="publishers", to="games.game")),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("team", models.TextField(blank=True, null=True)),
                ("role", models.TextField(blank=True, null=True)),
                (
                    "outcome",
                    models.PositiveSmallIntegerField(
                        blank=True, choices=[(0, "win"), (1, "draw"), (2, "lose"), (3, "withdrawal")], null=True
                    ),
                ),
                ("victory_type", models.TextField(blank=True, null=True)),
                ("match", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.match")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.TextField()),
                ("person_role", models.PositiveSmallIntegerField(choices=[(1, "Designer"), (2, "Artist")])),
                ("games", models.ManyToManyField(related_name="people", to="games.game")),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("recipients", models.ManyToManyField(related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("chat", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.chat")),
                (
                    "sender",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MatchProposal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("proposed_time", models.DateTimeField()),
                ("min_players", models.PositiveIntegerField()),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="users.group")),
                (
                    "joined",
                    models.ManyToManyField(blank=True, related_name="joined_matches", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "proposer",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.AddField(
            model_name="match",
            name="players",
            field=models.ManyToManyField(through="games.Player", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="game",
            name="mechanics",
            field=models.ManyToManyField(related_name="games", to="games.mechanic"),
        ),
        migrations.AddField(
            model_name="chat",
            name="match",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="games.match"),
        ),
    ]
