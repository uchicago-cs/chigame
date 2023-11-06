# Generated by Django 4.2.4 on 2023-11-06 21:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0002_lobby"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lobby",
            name="game_modification_status",
            field=models.PositiveSmallIntegerField(choices=[(1, "Default Game"), (2, "Modified Game")], default=1),
        ),
        migrations.AlterField(
            model_name="lobby",
            name="match_status",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Lobbied"), (2, "In-Progress"), (3, "Finished")], default=1
            ),
        ),
    ]
