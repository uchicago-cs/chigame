from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_livechatmessagereaction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="livechatmessagereaction",
            name="content",
            field=models.CharField(help_text="Up to 10 emoji characters", max_length=10),
        ),
    ]
