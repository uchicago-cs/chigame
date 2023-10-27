# Generated by Django 4.2.4 on 2023-10-27 18:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0002_initial"),
    ]

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
                ("name", models.TextField()),
                ("min_players", models.PositiveIntegerField()),
                ("max_players", models.PositiveIntegerField()),
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
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("lobby", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="games.lobby")),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("match", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.match")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
            model_name="match",
            name="winners",
            field=models.ManyToManyField(blank=True, related_name="won_matches", to=settings.AUTH_USER_MODEL),
        ),
    ]
