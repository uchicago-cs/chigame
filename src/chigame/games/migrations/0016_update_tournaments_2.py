# Generated by Django 4.2.4 on 2023-11-17 01:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0015_message_token_id_message_update_on_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tournament",
            old_name="end_date",
            new_name="tournament_end_date",
        ),
        migrations.RenameField(
            model_name="tournament",
            old_name="start_date",
            new_name="tournament_start_date",
        ),
        migrations.AddField(
            model_name="tournament",
            name="archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="tournament",
            name="registration_end_date",
            field=models.DateTimeField(),
        ),
        migrations.AddField(
            model_name="tournament",
            name="registration_start_date",
            field=models.DateTimeField(),
        ),
    ]
