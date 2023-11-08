# Generated by Django 4.2.4 on 2023-11-03 00:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0001_games_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="BGG_id",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="complexity",
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="expected_playtime",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="image",
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="max_playtime",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="min_playtime",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="rules",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="year_published",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.CreateModel(
            name="People",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "person_type",
                    models.PositiveSmallIntegerField(choices=[(1, "Designers"), (2, "Publishers"), (3, "Artists")]),
                ),
                ("name", models.TextField()),
                ("game", models.ManyToManyField(to="games.game")),
            ],
        ),
    ]