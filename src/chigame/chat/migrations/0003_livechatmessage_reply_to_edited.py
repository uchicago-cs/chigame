# Generated manually to fix migration conflicts

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_livechatmessagereaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="livechatmessage",
            name="reply_to",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="chat.livechatmessage"
            ),
        ),
        migrations.AddField(
            model_name="livechatmessage",
            name="edited",
            field=models.BooleanField(default=False),
        ),
    ] 