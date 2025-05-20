# Generated manually to fix migration conflicts

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0003_livechatmessagereaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="livechatmessage",
            name="edited",
            field=models.BooleanField(default=False),
        ),
    ] 