# Generated by Django 4.2.4 on 2023-11-10 21:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0006_Allow_null_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="image",
            field=models.TextField(default="/static/images/no_picture_available.png"),
        ),
        migrations.AlterField(
            model_name="game",
            name="rules",
            field=models.TextField(blank=True, null=True),
        ),
    ]
