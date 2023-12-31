# Generated by Django 4.2.4 on 2023-11-28 04:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0017_merge_20231127_2228"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(2023, 11, 28, 4, 50, 25, 750080, tzinfo=datetime.timezone.utc),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="review",
            name="title",
            field=models.TextField(blank=True, null=True),
        ),
    ]
