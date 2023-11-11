# Generated by Django 4.2.4 on 2023-11-07 06:27

from django.conf import settings

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("games", "0003_category_mechanic_game_bgg_id_game_complexity_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notification",
            old_name="receipients",
            new_name="recipients",
        ),
        migrations.AlterField(
            model_name="message",
            name="sender",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
