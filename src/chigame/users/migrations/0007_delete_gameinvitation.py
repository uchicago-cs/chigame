# Generated by Django 4.2.4 on 2023-12-06 21:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_merge_20231205_1748"),
    ]

    operations = [
        migrations.DeleteModel(
            name="GameInvitation",
        ),
    ]