# Generated by Django 4.2.4 on 2023-11-15 00:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0010_categories_plural"),
    ]

    operations = [
        migrations.RenameField(
            model_name="game",
            old_name="categories",
            new_name="category",
        ),
    ]
