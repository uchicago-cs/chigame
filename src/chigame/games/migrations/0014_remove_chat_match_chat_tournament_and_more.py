# Generated by Django 4.2.4 on 2023-11-24 21:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0013_merge_20231116_0044"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chat",
            name="match",
        ),
        migrations.AddField(
            model_name="chat",
            name="tournament",
            field=models.OneToOneField(
                default=None, on_delete=django.db.models.deletion.CASCADE, to="games.tournament"
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="year_published",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
