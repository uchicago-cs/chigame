# Generated by Django 4.2.4 on 2023-11-30 08:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum_conversation", "0018_post_ratings_vote_post_vote_poster"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="vote",
            constraint=models.UniqueConstraint(fields=("poster", "post"), name="unique_rating"),
        ),
    ]
