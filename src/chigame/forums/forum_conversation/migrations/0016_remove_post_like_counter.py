# Generated by Django 4.2.4 on 2023-11-29 21:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("forum_conversation", "0015_post_like_counter"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="like_counter",
        ),
    ]
