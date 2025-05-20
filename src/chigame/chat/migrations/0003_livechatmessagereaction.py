# Generated manually to fix migration conflicts

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_livechatmessage_reply_to"),
    ]

    operations = [
        # This was a duplicate model creation that's now handled by 0002_livechatmessagereaction.py
        # We're leaving this as a no-op migration to maintain migration history
    ] 